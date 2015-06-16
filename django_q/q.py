import importlib
from random import randint
from multiprocessing import Queue, Process, Event, current_process, cpu_count
import sys
import signal
import logging
from time import sleep

import jsonpickle as json

import coloredlogs
import redis
from django.conf import settings
from django.utils import timezone

from .models import Task

from .humanhash import uuid

r = redis.StrictRedis(decode_responses=True)
secret = settings.SECRET_KEY
prefix = 'django_q'
q_list = '{}:q'.format(prefix)

logger = logging.getLogger('django-q')
coloredlogs.install(level=logging.INFO)


def test():
    for i in range(20):
        defer(u'testq.tasks.multiply', 5, i * randint(2, 100))


def defer(func, *args, **kwargs):
    # [name, func, args, kwargs, started, finished, result]
    pack = json.dumps([uuid()[0], func, args, kwargs, timezone.now()])
    r.rpush(q_list, pack)
    logger.debug('Pushed {}'.format(pack))


class Worker(object):
    def __init__(self):
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        self.running = True
        self.stable_size = cpu_count()
        self.stable = []
        self.task_queue = Queue()
        self.done_queue = Queue()
        self.fail_queue = Queue()
        # Spawn work horses
        for i in range(self.stable_size):
            self.spawn_horse()
        # Spawn monitors
        self.success_monitor_pid = None
        self.spawn_success_monitor()
        self.failure_monitor_pid = None
        self.spawn_failure_monitor()
        # Spawn pusher
        self.pusher_pid = None
        self.pusher_stop = Event()
        self.spawn_pusher()
        # Monitor process health
        while self.running:
            self.stable_boy()
            sleep(1)

    def spawn_process(self, target, *args):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close
        p = Process(target=target, args=args)
        self.stable.append(p)
        p.start()
        return p.pid

    def spawn_pusher(self):
        self.pusher_pid = self.spawn_process(self.pusher, self.task_queue, self.pusher_stop)

    def spawn_horse(self):
        self.spawn_process(self.horse, self.task_queue, self.done_queue, self.fail_queue)

    def spawn_success_monitor(self):
        self.success_monitor_pid = self.spawn_process(self.success_monitor, self.done_queue)

    def spawn_failure_monitor(self):
        self.failure_monitor_pid = self.spawn_process(self.failure_monitor, self.fail_queue)

    def reincarnate(self, pid):
        if pid == self.success_monitor_pid:
            self.spawn_success_monitor()
            logger.warn("reincarnated success monitor after death of {}".format(pid))
        elif pid == self.failure_monitor_pid:
            self.spawn_failure_monitor()
            logger.warn("reincarnated failure monitor after death of {}".format(pid))
        else:
            self.spawn_horse()
            logger.warn("reincarnated work horse after death of {}".format(pid))

    @staticmethod
    def pusher(task_queue, e):
        logger.info('{} pushing tasks at {}'.format(current_process().name, current_process().pid))
        while not e.is_set():
            task = r.blpop(q_list, 1)
            if task:
                task_queue.put(task[1])
                logger.debug('queueing {}'.format(task[1]))

    @staticmethod
    def success_monitor(done_queue):
        name = current_process().name
        logger.info("{} monitoring successes at {}".format(name, current_process().pid))
        for task in iter(done_queue.get, 'STOP'):
            logger.info("Finished [{}:{}]".format(task[1], task[0]))
            Task.objects.create(name=task[0], func=task[1], task=json.dumps(task),
                                started=task[4],
                                stopped=task[5])
        logger.info("{} stopped".format(name))

    @staticmethod
    def failure_monitor(fail_queue):
        name = current_process().name
        logger.info("{} monitoring failures at {}".format(name, current_process().pid))
        for task in iter(fail_queue.get, 'STOP'):
            logger.error("Failure [{}:{} - {}]".format(task[1], task[0], task[6]))
            Task.objects.create(name=task[0], func=task[1], task=json.dumps(task),
                                started=task[4],
                                stopped=task[5], success=False)
        logger.info("{} stopped".format(name))

    @staticmethod
    def horse(task_queue, done_queue, fail_queue):
        name = current_process().name
        logger.info('{} ready for work at {}'.format(name, current_process().pid))
        for pack in iter(task_queue.get, 'STOP'):
            try:
                task = json.loads(pack)
            except TypeError as e:
                logger.error(e)
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
                done_queue.put(task)
            except TypeError as e:
                task.append(e)
                fail_queue.put(task)
        logger.info('{} Stopped'.format(name))

    def stable_boy(self):
        # Check if all the horses are alive
        for p in list(self.stable):
            if not p.is_alive():
                # Be humane
                p.terminate()
                self.stable.remove(p)
                # Replace it with a fresh one
                self.reincarnate(p.pid)

    def stop(self):
        # Send the STOP signal to the stable
        self.running = False
        logger.info('Stopping')
        # Wait for all the workers to finish the queue
        for p in self.stable:
            if p.pid == self.failure_monitor_pid:
                self.fail_queue.put('STOP')
            elif p.pid == self.success_monitor_pid:
                self.done_queue.put('STOP')
            elif p.pid == self.pusher_pid:
                self.pusher_stop.set()
            else:
                self.task_queue.put('STOP')
            p.join()

        logger.info('Goodbye. Have a wonderful time.')

    def sig_handler(self, signum, frame):
        self.stop()
