import importlib
import logging
import pickle
import signal
from multiprocessing import cpu_count, Queue, Event, Process, current_process
import sys
from time import sleep

import coloredlogs

from django.utils import timezone
import redis

from django.core.signing import Signer, BadSignature

from django_q.apps import LOG_LEVEL, SECRET_KEY, SAVE_LIMIT
from django_q.humanhash import uuid
from django_q.models import Task, Success

prefix = 'django_q'
q_list = '{}:q'.format(prefix)
signer = Signer(SECRET_KEY)
logger = logging.getLogger('django-q')
coloredlogs.install(level=getattr(logging, LOG_LEVEL))

r = redis.StrictRedis()


class Cluster(object):
    def __init__(self):
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        try:
            r.ping()
        except ():
            logger.error('Can not connect to Redis server')
            return
        self.running = True
        self.pool_size = cpu_count()
        self.pool = []
        self.task_queue = Queue()
        self.done_queue = Queue()
        # Spawn workers
        for i in range(self.pool_size):
            self.spawn_worker()
        # Spawn monitor
        self.monitor_pid = None
        self.spawn_monitor()
        # Spawn pusher
        self.pusher_pid = None
        self.pusher_stop = Event()
        self.spawn_pusher()
        # Monitor process health
        while self.running:
            self.medic()
            sleep(1)

    def spawn_process(self, target, *args):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close
        p = Process(target=target, args=args)
        self.pool.append(p)
        p.start()
        return p.pid

    def spawn_pusher(self):
        self.pusher_pid = self.spawn_process(self.pusher, self.task_queue, self.pusher_stop)

    def spawn_worker(self):
        self.spawn_process(self.worker, self.task_queue, self.done_queue)

    def spawn_monitor(self):
        self.monitor_pid = self.spawn_process(self.monitor, self.done_queue)

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

    @staticmethod
    def pusher(task_queue, e):
        logger.info('{} pushing tasks at {}'.format(current_process().name, current_process().pid))
        while not e.is_set():
            task = r.blpop(q_list, 1)
            if task:
                task = task[1]
                task_queue.put(task)
                logger.debug('queueing {}'.format(task))

    @staticmethod
    def monitor(done_queue):
        name = current_process().name
        logger.info("{} monitoring at {}".format(name, current_process().pid))
        for task in iter(done_queue.get, 'STOP'):
            name = task[0]
            func = task[1]
            result = task[6]
            success = task[7]
            if success:
                logger.info("Finished [{}:{}]".format(func, name))
            else:
                logger.error("Failed [{}:{}] - {}".format(func, name, result))
            Cluster.save_task(task)
        logger.info("{} stopped".format(name))

    @staticmethod
    def worker(task_queue, done_queue):
        name = current_process().name
        logger.info('{} ready for work at {}'.format(name, current_process().pid))
        for pack in iter(task_queue.get, 'STOP'):
            # unpickle the task
            try:
                task = pickle.loads(pack)
            except TypeError as e:
                logger.error(e)
                continue
            # check signature
            try:
                task[0] = signer.unsign(task[0])
            except BadSignature as e:
                task[0] = task[0].rsplit(":", 1)[0]
                task.append(timezone.now())
                task.append(e)
                task.append(False)
                done_queue.put(task)
                continue
            func = task[1]
            module, func = func.rsplit('.', 1)
            args = task[2]
            kwargs = task[3]
            logger.info('{} processing [{}:{}]'.format(name, func, task[0]))
            task.append(timezone.now())
            try:
                m = importlib.import_module(module)
                f = getattr(m, func)
                result = f(*args, **kwargs)
                task.append(result)
                task.append(True)
                done_queue.put(task)
            except Exception as e:
                task.append(e)
                task.append(False)
                done_queue.put(task)
        logger.info('{} Stopped'.format(name))

    def medic(self):
        # Check if all the workers are alive
        for p in list(self.pool):
            if not p.is_alive():
                # Be humane
                p.terminate()
                self.pool.remove(p)
                # Replace it with a fresh one
                self.reincarnate(p.pid)

    @staticmethod
    def save_task(task):
        if task[7] and 0 < SAVE_LIMIT < Success.objects.count():
            Success.objects.first().delete()
        Task.objects.create(name=task[0],
                            func=task[1],
                            args=task[2],
                            kwargs=task[3],
                            started=task[4],
                            stopped=task[5],
                            result=task[6],
                            success=task[7])

    def stop(self):
        # Send the STOP signal to the pool
        self.running = False
        logger.info('Stopping')
        # Wait for all the workers to finish the queue
        for p in self.pool:
            if p.pid == self.monitor_pid:
                self.done_queue.put('STOP')
            elif p.pid == self.pusher_pid:
                self.pusher_stop.set()
            else:
                self.task_queue.put('STOP')
            p.join()

        logger.info('Goodbye. Have a wonderful time.')

    def sig_handler(self, signum, frame):
        self.stop()


def async(func, *args, **kwargs):
    # [name, func, args, kwargs, started, finished, result, success]
    name = signer.sign(uuid()[0])
    pack = pickle.dumps([name, func, args, kwargs, timezone.now()])
    r.rpush(q_list, pack)
    logger.debug('Pushed {}'.format(pack))
    return name
