import importlib
from time import sleep
from multiprocessing import Queue, Process, current_process, cpu_count
import sys
import signal

import redis
from django.conf import settings

try:
    import cPickle as pickle
except ImportError:
    import pickle

r = redis.StrictRedis()
secret = settings.SECRET_KEY
prefix = 'django_q'
q_list = '{}:q'.format(prefix)


def test():
    for i in range(20):
        defer('testq.tasks.multiply', 5, i)


def defer(func, *args, **kwargs):
    # serialize the func
    task = {u'func': func, u'args': args, u'kwargs': kwargs}
    pack = pickle.dumps(task)
    r.rpush(q_list, pack)


class Worker(object):
    def __init__(self):
        self.running = True
        self.stable_size = cpu_count()
        self.stable = []
        self.task_queue = Queue()
        self.done_queue = Queue()
        # Spawn work horses
        for i in range(self.stable_size):
            self._spawn_horse()
        # Spawn monitor
        self._spawn_monitor()
        # Attach signal handler
        signal.signal(signal.SIGTERM, self.sighandler)
        signal.signal(signal.SIGINT, self.sighandler)
        # Keep popping Redis
        while self.running:
            self.work()
            sleep(0.2)

    def _spawn_horse(self):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close

        p = Process(target=self.horse, args=(self.task_queue, self.done_queue))
        self.stable.append(p)
        p.start()

    def _spawn_monitor(self):
        # This is just for PyCharm to not crash. Ignore it.
        if not hasattr(sys.stdin, 'close'):
            def dummy_close():
                pass

            sys.stdin.close = dummy_close

        self.mon = Process(target=self.monitor, args=(self.done_queue,))
        self.mon.start()

    @staticmethod
    def monitor(queue_in):
        print("Monitor started at {}".format(current_process().pid))
        for result in iter(queue_in.get, 'STOP'):
            task = result['task']
            res = result['result']
            print("{} - {}".format(task['func'], res))
        print("Monitor stopped")

    @staticmethod
    def horse(queue_in, queue_out):
        name = current_process().name
        print(name, 'Ready for work at {}'.format(current_process().pid))
        for pack in iter(queue_in.get, 'STOP'):
            task = pickle.loads(pack)
            func = task['func']
            module, func = func.rsplit('.', 1)
            args = task['args']
            kwargs = task['kwargs']
            print(name, 'Starting Task {}'.format(func))
            try:
                m = importlib.import_module(module)
                f = getattr(m, func)
                result = f(*args, **kwargs)
                queue_out.put({'task': task, 'result': result})
                print(name, 'Finished JTask {}'.format(func))
            except TypeError:
                print('job failed')
                # TODO log failure to django
        print(name, 'Stopped')

    def work(self):
        self.stable_boy()
        self.task_queue.put(r.brpop(q_list))

    def stable_boy(self):
        # Check if all the horses are alive
        for p in list(self.stable):
            if not p.is_alive():
                # Be humane
                p.terminate()
                self.stable.remove(p)
                # Replace it with a fresh one
                self._spawn_horse()

    def stop(self):
        # Send the STOP signal to the stable
        self.running = False
        print('Stopping queue')
        for i in range(self.stable_size):
            self.task_queue.put('STOP')
            # Optional: Delete everything in the queue and then add STOP
        self.done_queue.put('STOP')
        # Wait for all the workers to finish the queue
        for p in self.stable:
            p.join()
        self.mon.join()
        print('All horses stopped.')
        print('Goodbye. Have a wonderful time.')

    def sighandler(self, signum, frame):
        self.stop()
