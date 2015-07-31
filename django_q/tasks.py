"""Provides task functionalities."""
from multiprocessing import Queue, Value

# django
from django.utils import timezone

# local
import signing
import cluster
from django_q.conf import Conf, redis_client, logger
from django_q.models import Schedule, Task
from django_q.humanhash import uuid


def async(func, *args, **kwargs):
    """Send a task to the cluster."""
    # get options from q_options dict or direct from kwargs
    options = kwargs.pop('q_options', kwargs)
    hook = options.pop('hook', None)
    list_key = options.pop('list_key', Conf.Q_LIST)
    redis = options.pop('redis', redis_client)
    sync = options.pop('sync', False)
    group = options.pop('group', None)
    save = options.pop('save', None)
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
    # sign it
    pack = signing.SignedPackage.dumps(task)
    if sync:
        return _sync(pack)
    # push it
    redis.rpush(list_key, pack)
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
    repeats = kwargs.pop('repeats', -1)
    next_run = kwargs.pop('next_run', timezone.now())

    return Schedule.objects.create(name=name,
                                   func=func,
                                   hook=hook,
                                   args=args,
                                   kwargs=kwargs,
                                   schedule_type=schedule_type,
                                   repeats=repeats,
                                   next_run=next_run
                                   )


def result(task_id):
    """
    Return the result of the named task.

    :type task_id: str or uuid
    :param task_id: the task name or uuid
    :return: the result object of this task
    :rtype: object
    """
    return Task.get_result(task_id)


def result_group(group_id, failures=False):
    """
    Return a list of results for a task group.

    :param str group_id: the group id
    :param bool failures: set to True to include failures
    :return: list or results
    """
    return Task.get_result_group(group_id, failures)


def fetch(task_id):
    """
    Return the processed task.

    :param task_id: the task name or uuid
    :type task_id: str or uuid
    :return: the full task object
    :rtype: Task
    """
    return Task.get_task(task_id)


def fetch_group(group_id, failures=True):
    """
    Return a list of Tasks for a task group.

    :param str group_id: the group id
    :param bool failures: set to False to exclude failures
    :return: list of Tasks
    """
    return Task.get_task_group(group_id, failures)


def count_group(group_id, failures=False):
    """
    Count the results in a group.

    :param str group_id: the group id
    :param bool failures: Returns failure count if True
    :return: the number of tasks/results in a group
    :rtype: int
    """
    return Task.get_group_count(group_id, failures)


def delete_group(group_id, tasks=False):
    """
    Delete a group.

    :param str group_id: the group id
    :param bool tasks: If set to True this will also delete the group tasks.
    Otherwise just the group label is removed.
    :return:
    """
    return Task.delete_group(group_id, tasks)


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
