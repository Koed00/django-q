import importlib
import logging
import os
import signal
from multiprocessing import Queue, Event, Process, current_process
import sys
from time import sleep

# External
import jsonpickle
import coloredlogs
import redis

# Django
from django.core import signing

from django.utils import timezone

# Local
from .conf import LOG_LEVEL, SECRET_KEY, SAVE_LIMIT, WORKERS, COMPRESSED, VERSION
from .humanhash import uuid
from .models import Task, Success

SIGNAL_NAMES = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n)

prefix = 'django_q'
q_list = '{}:q'.format(prefix)
logger = logging.getLogger('django-q')
coloredlogs.install(level=getattr(logging, LOG_LEVEL))

r = redis.StrictRedis()


class Cluster(object):
    def __init__(self):
        try:
            r.ping()
        except ():
            logger.error('Can not connect to Redis server')
            return
        self.sentinel = None
        self.stop_event = None
        self.pid = current_process().pid
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

    def start(self):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close
        # Start Sentinel
        self.stop_event = Event()
        self.sentinel = Process(target=Sentinel, args=(self.stop_event,))
        self.sentinel.start()
        logger.info('Starting Q cluster version {} at {}'.format(VERSION, self.pid))

    def stop(self):
        self.stop_event.set()
        self.sentinel.join()
        logger.info('Q cluster has stopped.')

    def stats(self):
        return Stat.load(self.pid)

    def sig_handler(self, signum, frame):
        logger.debug('{} got signal {}'.format(current_process().name, SIGNAL_NAMES.get(signum, 'UNKNOWN')))
        self.stop()


class Sentinel(object):
    def __init__(self, event):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        self.pid = current_process().pid
        self.parent_pid = os.getppid()
        self.name = current_process().name
        self.status = 'Initializing'
        self.tob = timezone.now()
        self.stop_event = event
        self.pool_size = WORKERS
        self.pool = []
        self.task_queue = Queue()
        self.done_queue = Queue()
        self.event_out = Event()
        self.monitor_pid = None
        self.pusher_pid = None
        self.spawn_cluster()
        self.guard()

    def spawn_process(self, target, *args):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close
        p = Process(target=target, args=args)
        p.daemon = True
        self.pool.append(p)
        p.start()
        return p.pid

    def spawn_pusher(self):
        return self.spawn_process(pusher, self.task_queue, self.event_out)

    def spawn_worker(self):
        self.spawn_process(worker, self.task_queue, self.done_queue)

    def spawn_monitor(self):
        return self.spawn_process(monitor, self.done_queue)

    def reincarnate(self, pid):
        if pid == self.monitor_pid:
            self.spawn_monitor()
            logger.warn("reincarnated monitor after death of {}".format(pid))
        elif pid == self.pusher_pid:
            self.spawn_pusher()
            logger.warn("reincarnated pusher after death of {}".format(pid))
        else:
            self.spawn_worker()
            logger.warn("reincarnated work worker after death of {}".format(pid))

    def spawn_cluster(self):
        for i in range(self.pool_size):
            self.spawn_worker()
        self.monitor_pid = self.spawn_monitor()
        self.pusher_pid = self.spawn_pusher()

    def guard(self):
        logger.info('{} guarding cluster at {}'.format(current_process().name, self.pid))
        self.status = 'Running'
        while not self.stop_event.is_set():
            for p in list(self.pool):
                if not p.is_alive():
                    # Be humane
                    p.terminate()
                    self.pool.remove(p)
                    # Replace it with a fresh one
                    self.reincarnate(p.pid)
            self.stats()
            sleep(1)
        self.stop()

    def stats(self):
        Stat(self).save()

    def stop(self):
        self.status = 'Stopping'
        # Send the STOP signal to the pool
        name = current_process().name
        logger.info('{} stopping pool processes'.format(name))
        # Stopping pusher
        self.event_out.set()
        # Putting poison pills in the queue
        for _ in self.pool:
            self.task_queue.put('STOP')
        while len(self.pool) > 2:
            for p in list(self.pool):
                if not p.is_alive():
                    logger.debug('{} stopped gracefully'.format(p.pid))
                    self.pool.remove(p)
            sleep(0.2)
        # Finally stop the monitor
        self.done_queue.put('STOP')
        self.pool = []
        self.status = 'Stopped'


def pusher(task_queue, e):
    logger.info('{} pushing tasks at {}'.format(current_process().name, current_process().pid))
    while not e.is_set():
        task = r.blpop(q_list, 1)
        if task:
            task = task[1]
            task_queue.put(task)
            logger.debug('queueing {}'.format(task))
    logger.info("{} stopped pushing tasks".format(current_process().name))


def monitor(done_queue):
    name = current_process().name
    logger.info("{} monitoring results at {}".format(name, current_process().pid))
    for task in iter(done_queue.get, 'STOP'):
        if task['success']:
            logger.info("Finished [{}:{}]".format(task['func'], task['name']))
        else:
            logger.error("Failed [{}:{}] - {}".format(task['func'], task['name'], task['result']))
        save_task(task)
    logger.info("{} stopped monitoring results".format(name))


def worker(task_queue, done_queue):
    name = current_process().name
    logger.info('{} ready for work at {}'.format(name, current_process().pid))
    for pack in iter(task_queue.get, 'STOP'):
        # unpickle the task
        try:
            task = SignedPackage.loads(pack)
        except TypeError as e:
            logger.error(e)
            continue
        except signing.BadSignature as e:
            task['name'] = task['name'].rsplit(":", 1)[0]
            task['stopped'] = timezone.now()
            task['result'] = e
            task['success'] = False
            done_queue.put(task)
            continue
        module, func = task['func'].rsplit('.', 1)
        logger.info('{} processing [{}:{}]'.format(name, task['func'], task['name']))
        try:
            m = importlib.import_module(module)
            f = getattr(m, func)
            task['result'] = f(*task['args'], **task['kwargs'])
            task['stopped'] = timezone.now()
            task['success'] = True
            done_queue.put(task)
        except Exception as e:
            task['result'] = e
            task['stopped'] = timezone.now()
            task['success'] = False
            done_queue.put(task)
    logger.info('{} stopped doing work'.format(name))


def save_task(task):
    if task['success'] and 0 < SAVE_LIMIT < Success.objects.count():
        Success.objects.first().delete()
    Task.objects.create(name=task['name'],
                        func=task['func'],
                        hook=task['hook'],
                        args=task['args'],
                        kwargs=task['kwargs'],
                        started=task['started'],
                        stopped=task['stopped'],
                        result=task['result'],
                        success=task['success'])


def async(func, *args, hook=None, **kwargs):
    """
    Schedules a task
    """
    task = {'name': uuid()[0], 'func': func, 'hook': hook, 'args': args, 'kwargs': kwargs, 'started': timezone.now()}
    pack = SignedPackage.dumps(task)
    r.rpush(q_list, pack)
    logger.debug('Pushed {}'.format(pack))
    return task['name']


class SignedPackage(object):
    """
    Wraps Django's signing module with custom JsonPickle serializer
    """

    @staticmethod
    def dumps(obj, compressed=COMPRESSED):
        return signing.dumps(obj,
                             key=SECRET_KEY,
                             salt='django_q.q',
                             compress=compressed,
                             serializer=JSONPickleSerializer)

    @staticmethod
    def loads(obj):
        return signing.loads(obj,
                             key=SECRET_KEY,
                             salt='django_q.q',
                             serializer=JSONPickleSerializer)


class JSONPickleSerializer(object):
    """
    Simple wrapper around JsonPickle for signing.dumps and
    signing.loads.
    """

    @staticmethod
    def dumps(obj):
        return jsonpickle.dumps(obj).encode('latin-1')

    @staticmethod
    def loads(data):
        return jsonpickle.loads(data.decode('latin-1'))


class Stat(object):
    def __init__(self, sentinel):
        self.cluster_id = sentinel.parent_pid
        self.status = sentinel.status
        self.sentinel = sentinel.pid
        self.monitor = sentinel.monitor_pid
        self.pusher = sentinel.pusher_pid
        self.workers = []
        for w in sentinel.pool:
            self.workers.append(w.pid)
        self.task_q_size = sentinel.task_queue.qsize()
        self.done_q_size = sentinel.done_queue.qsize()
        self.tob = sentinel.tob
        self.timestamp = timezone.now()

    @property
    def key(self):
        return self.get_key(self.cluster_id)

    @staticmethod
    def get_key(cluster_id):
        return '{}:cluster:{}'.format(prefix, cluster_id)

    def save(self):
        r.set(self.key, SignedPackage.dumps(self, True), 5)

    @staticmethod
    def load(cluster_id=None):
        if not cluster_id:
            stats = []
            keys = r.keys(pattern='{}:cluster:*'.format(prefix))
            if not keys:
                return None
            packs = r.mget(keys)
            for pack in packs:
                try:
                    stats.append(SignedPackage.loads(pack))
                except signing.BadSignature:
                    continue
            return stats
        else:
            pack = r.get(Stat.get_key(cluster_id))
            if pack:
                try:
                    return SignedPackage.loads(pack)
                except signing.BadSignature:
                    return None
            return None
