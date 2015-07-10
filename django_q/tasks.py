from multiprocessing import Queue, Value

try:
    import cPickle as pickle
except ImportError:
    import pickle

# django
from django.utils import timezone

# local
import signing
import cluster
from django_q.conf import Conf, redis_client, logger
from django_q.models import Schedule, Task
from django_q.humanhash import uuid


def async(func, *args, **kwargs):
    """
    Sends a task to the cluster
    """
    # optional hook
    hook = kwargs.pop('hook', None)
    # optional list_key
    list_key = kwargs.pop('list_key', Conf.Q_LIST)
    # optional redis connection
    r = kwargs.pop('redis', redis_client)
    # optional sync mode
    s = kwargs.pop('sync', False)
    # get an id
    tag = uuid()
    # build the task package
    task = {'id': tag[1], 'name': tag[0], 'func': func, 'hook': hook, 'args': args, 'kwargs': kwargs,
            'started': timezone.now()}
    # sign it
    pack = signing.SignedPackage.dumps(task)
    if s:
        return _sync(task['id'], pack)
    # push it
    r.rpush(list_key, pack)
    logger.debug('Pushed {}'.format(tag))
    return task['id']


def schedule(func, *args, **kwargs):
    """
    :param func: function to schedule
    :param args: function arguments
    :param hook: optional result hook function
    :type schedule_type: Schedule.TYPE
    :param repeats: how many times to repeat. 0=never, -1=always
    :param next_run: Next scheduled run
    :type next_run: datetime.datetime
    :param kwargs: function keyword arguments
    :return: the schedule object
    :rtype: Schedule
    """

    hook = kwargs.pop('hook', None)
    schedule_type = kwargs.pop('schedule_type', Schedule.ONCE)
    repeats = kwargs.pop('repeats', -1)
    next_run = kwargs.pop('next_run', timezone.now())

    return Schedule.objects.create(func=func,
                                   hook=hook,
                                   args=args,
                                   kwargs=kwargs,
                                   schedule_type=schedule_type,
                                   repeats=repeats,
                                   next_run=next_run
                                   )


def result(task_id):
    """
    Returns the result of the named task
    :type task_id: str or uuid
    :param task_id: the task name or uuid
    :return: the result object of this task
    :rtype: object
    """
    return Task.get_result(task_id)


def fetch(task_id):
    """
    Returns the processed task
    :param task_id: the task name or uuid
    :type task_id: str or uuid
    :return: the full task object
    :rtype: Task
    """
    return Task.get_task(task_id)


def _sync(task_id, pack):
    """
    Simulates a package travelling through the cluster.

    """
    task_queue = Queue()
    result_queue = Queue()
    task_queue.put(pack)
    task_queue.put('STOP')
    cluster.worker(task_queue, result_queue, Value('b', -1))
    result_queue.put('STOP')
    cluster.monitor(result_queue)
    return task_id
