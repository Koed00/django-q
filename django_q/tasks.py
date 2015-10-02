"""Provides task functionality."""
from multiprocessing import Queue, Value

# django
from django.utils import timezone

# local
import time
import signing
import cluster
from django_q.conf import Conf, logger
from django_q.models import Schedule, Task
from django_q.humanhash import uuid
from django_q.brokers import get_broker


def async(func, *args, **kwargs):
    """Send a task to the cluster."""
    # get options from q_options dict or direct from kwargs
    options = kwargs.pop('q_options', kwargs)
    hook = options.pop('hook', None)
    broker = options.pop('broker', get_broker())
    sync = options.pop('sync', False)
    group = options.pop('group', None)
    save = options.pop('save', None)
    cached = options.pop('cached', Conf.CACHED)
    # get an id
    tag = uuid()
    # build the task package
    task = {'id': tag[1], 'name': tag[0],
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'started': timezone.now()}
    # add optionals
    if hook:
        task['hook'] = hook
    if group:
        task['group'] = group
    if save is not None:
        task['save'] = save
    if cached:
        task['cached'] = cached
    # sign it
    pack = signing.SignedPackage.dumps(task)
    if sync or Conf.SYNC:
        return _sync(pack)
    # push it
    broker.enqueue(pack)
    logger.debug('Pushed {}'.format(tag))
    return task['id']


def schedule(func, *args, **kwargs):
    """
    Create a schedule.

    :param func: function to schedule.
    :param args: function arguments.
    :param name: optional name for the schedule.
    :param hook: optional result hook function.
    :type schedule_type: Schedule.TYPE
    :param repeats: how many times to repeat. 0=never, -1=always.
    :param next_run: Next scheduled run.
    :type next_run: datetime.datetime
    :param kwargs: function keyword arguments.
    :return: the schedule object.
    :rtype: Schedule
    """
    name = kwargs.pop('name', None)
    hook = kwargs.pop('hook', None)
    schedule_type = kwargs.pop('schedule_type', Schedule.ONCE)
    minutes = kwargs.pop('minutes', None)
    repeats = kwargs.pop('repeats', -1)
    next_run = kwargs.pop('next_run', timezone.now())

    return Schedule.objects.create(name=name,
                                   func=func,
                                   hook=hook,
                                   args=args,
                                   kwargs=kwargs,
                                   schedule_type=schedule_type,
                                   minutes=minutes,
                                   repeats=repeats,
                                   next_run=next_run
                                   )


def result(task_id, wait=0, cached=Conf.CACHED):
    """
    Return the result of the named task.

    :type task_id: str or uuid
    :param task_id: the task name or uuid
    :type wait: int
    :param wait: number of milliseconds to wait for a result
    :param cached: run this against the cache backend
    :return: the result object of this task
    :rtype: object
    """
    if cached:
        return result_cached(task_id, wait)
    start = time.time()
    while True:
        r = Task.get_result(task_id)
        if r:
            return r
        if (time.time() - start) * 1000 >= wait:
            break
        time.sleep(0.01)


def result_cached(task_id, wait=0, broker=None):
    """
     Return the result from the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    start = time.time()
    while True:
        r = broker.cache.get('{}:{}'.format(key, task_id))
        if r:
            return signing.SignedPackage.loads(r)['result']
        if (time.time() - start) * 1000 >= wait:
            break
        time.sleep(0.01)


def result_group(group_id, failures=False, cached=Conf.CACHED):
    """
    Return a list of results for a task group.

    :param str group_id: the group id
    :param bool failures: set to True to include failures
    :param cached: run this against the cache backend
    :return: list or results
    """
    if cached:
        return result_group_cached(group_id, failures)
    return Task.get_result_group(group_id, failures)


def result_group_cached(group_id, failures=False, broker=None):
    """
    Return a list of results for a task group from the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    group_list = broker.cache.get('{}:{}'.format(key, group_id))
    if group_list:
        result_list = []
        for task_package in group_list:
            task = signing.SignedPackage.loads(task_package)
            if task['success'] or failures:
                result_list.append(task['result'])
        return result_list


def fetch(task_id, wait=0, cached=Conf.CACHED):
    """
    Return the processed task.

    :param task_id: the task name or uuid
    :type task_id: str or uuid
    :param wait: the number of milliseconds to wait for a result
    :type wait: int
    :param cached: run this against the cache backend
    :return: the full task object
    :rtype: Task
    """
    if cached:
        return fetch_cached(task_id, wait)
    start = time.time()
    while True:
        t = Task.get_task(task_id)
        if t:
            return t
        if (time.time() - start) * 1000 >= wait:
            break
        time.sleep(0.01)


def fetch_cached(task_id, wait=0, broker=None):
    """
    Return the processed task from the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    start = time.time()
    while True:
        r = broker.cache.get('{}:{}'.format(key, task_id))
        if r:
            task = signing.SignedPackage.loads(r)
            t = Task(id=task['id'],
                     name=task['name'],
                     func=task['func'],
                     hook=task.get('hook'),
                     args=task['args'],
                     kwargs=task['kwargs'],
                     started=task['started'],
                     stopped=task['stopped'],
                     result=task['result'],
                     success=task['success'])
            return t
        if (time.time() - start) * 1000 >= wait:
            break
        time.sleep(0.01)


def fetch_group(group_id, failures=True, cached=Conf.CACHED):
    """
    Return a list of Tasks for a task group.

    :param str group_id: the group id
    :param bool failures: set to False to exclude failures
    :param cached: run this against the cache backend
    :return: list of Tasks
    """
    if cached:
        return fetch_group_cached(group_id, failures)
    return Task.get_task_group(group_id, failures)


def fetch_group_cached(group_id, failures=True, broker=None):
    """
    Return a list of Tasks for a task group in the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    group_list = broker.cache.get('{}:{}'.format(key, group_id))
    if group_list:
        task_list = []
        for task_package in group_list:
            task = signing.SignedPackage.loads(task_package)
            if task['success'] or failures:
                t = Task(id=task['id'],
                         name=task['name'],
                         func=task['func'],
                         hook=task.get('hook'),
                         args=task['args'],
                         kwargs=task['kwargs'],
                         started=task['started'],
                         stopped=task['stopped'],
                         result=task['result'],
                         group=task.get('group'),
                         success=task['success'])
                task_list.append(t)
        return task_list


def count_group(group_id, failures=False, cached=Conf.CACHED):
    """
    Count the results in a group.

    :param str group_id: the group id
    :param bool failures: Returns failure count if True
    :param cached: run this against the cache backend
    :return: the number of tasks/results in a group
    :rtype: int
    """
    if cached:
        return count_group_cached(group_id, failures)
    return Task.get_group_count(group_id, failures)


def count_group_cached(group_id, failures=False, broker=None):
    """
    Count the results in a group in the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    group_list = broker.cache.get('{}:{}'.format(key, group_id))
    if group_list:
        if not failures:
            return len(group_list)
        failure_count = 0
        for task_package in group_list:
            task = signing.SignedPackage.loads(task_package)
            if not task['success']:
                failure_count += 1
        return failure_count


def delete_group(group_id, tasks=False, cached=Conf.CACHED):
    """
    Delete a group.

    :param str group_id: the group id
    :param bool tasks: If set to True this will also delete the group tasks.
    Otherwise just the group label is removed.
    :param cached: run this against the cache backend
    :return:
    """
    if cached:
        return delete_group_cached(group_id)
    return Task.delete_group(group_id, tasks)


def delete_group_cached(group_id, broker=None):
    """
    Delete a group from the cache backend
    """
    if not broker:
        broker = get_broker()
    return delete_cached(group_id, broker)


def delete_cached(task_id, broker=None):
    """
    Delete a task from the cache backend
    """
    if not broker:
        broker = get_broker()
    key = 'django_q:{}:results'.format(broker.list_key)
    return broker.cache.delete('{}:{}'.format(key, task_id))


def queue_size(broker=None):
    """
    Returns the current queue size.
    Note that this doesn't count any tasks currently being processed by workers.

    :param broker: optional broker
    :return: current queue size
    :rtype: int
    """
    if not broker:
        broker = get_broker()
    return broker.queue_size()


def _sync(pack):
    """Simulate a package travelling through the cluster."""
    task_queue = Queue()
    result_queue = Queue()
    task = signing.SignedPackage.loads(pack)
    task_queue.put(task)
    task_queue.put('STOP')
    cluster.worker(task_queue, result_queue, Value('f', -1))
    result_queue.put('STOP')
    cluster.monitor(result_queue)
    return task['id']
