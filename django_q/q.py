import importlib
from time import sleep
from multiprocessing import Queue, Process, current_process, cpu_count
import sys
import signal
from uuid import uuid4
import ujson as json

import redis
from django.conf import settings

r = redis.StrictRedis(decode_responses=True)
secret = settings.SECRET_KEY
prefix = 'django_q'
q_list = '{}:q'.format(prefix)


def test():
    for i in range(4):
        defer(u'testq.tasks.multiply', 5, i)


def defer(func, *args, **kwargs):
    pack = json.dumps([uuid4().urn, func, args, kwargs])
    r.rpush(q_list, pack)


class Worker(object):
    def __init__(self):
        self.running = True
        self.stable_size = cpu_count() - 2
        self.stable = []
        self.task_queue = Queue()
        self.done_queue = Queue()
        self.fail_queue = Queue()
        self.failure_monitor_pid = None
        self.success_monitor_pid = None
        # Spawn work horses
        for i in range(self.stable_size):
            self.spawn_horse()
        # Spawn monitors
        self.spawn_success_monitor()
        self.spawn_failure_monitor()
        # Attach signal handler
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        # Keep popping Redis
        while self.running:
            self.stable_boy()
            sleep(0.2)
            task = r.lpop(q_list)
            if task:
                self.task_queue.put(task)

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

    def spawn_horse(self):
        self.spawn_process(self.horse, self.task_queue, self.done_queue, self.fail_queue)

    def spawn_success_monitor(self):
        self.success_monitor_pid = self.spawn_process(self.success_monitor, self.done_queue)

    def spawn_failure_monitor(self):
        self.failure_monitor_pid = self.spawn_process(self.failure_monitor, self.fail_queue)

    def reincarnate(self, pid):
        if pid == self.success_monitor_pid:
            self.spawn_success_monitor()
        elif pid == self.failure_monitor_pid:
            self.spawn_failure_monitor()
        else:
            self.spawn_horse()

    @staticmethod
    def success_monitor(done_queue):
        name = current_process().name
        print("{} monitoring successes at {}".format(name, current_process().pid))
        for result in iter(done_queue.get, 'STOP'):
            task = result[0]
            res = result[1]
            print("Success [{}:{} - {}]".format(task[1], task[0], res))
        print("{} stopped".format(name))

    @staticmethod
    def failure_monitor(fail_queue):
        name = current_process().name
        print("{} monitoring failures at {}".format(name, current_process().pid))
        for result in iter(fail_queue.get, 'STOP'):
            task = result[0]
            e = result[1]
            print("Failure [{}:{} - {}]".format(task[1], task[0], e))
        print("{} stopped".format(name))

    @staticmethod
    def horse(task_queue, done_queue, fail_queue):
        name = current_process().name
        print('{} ready for work at {}'.format(name, current_process().pid))
        for pack in iter(task_queue.get, 'STOP'):
            task = json.loads(pack)
            uid = task[0]
            func = task[1]
            module, func = func.rsplit('.', 1)
            args = task[2]
            kwargs = task[3]
            print(name, 'Processing [{}:{}]'.format(func, uid))
            try:
                m = importlib.import_module(module)
                f = getattr(m, func)
                result = f(*args, **kwargs)
                done_queue.put((task, result))
            except TypeError as e:
                fail_queue.put((task, e))
        print(name, 'Stopped')

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
        print('Stopping')
        # Wait for all the workers to finish the queue
        for p in self.stable:
            if p.pid == self.failure_monitor_pid:
                self.fail_queue.put('STOP')
            elif p.pid == self.success_monitor_pid:
                self.done_queue.put('STOP')
            else:
                self.task_queue.put('STOP')
            p.join()

        print('Goodbye. Have a wonderful time.')

    def sig_handler(self, signum, frame):
        self.stop()
