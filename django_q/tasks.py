try:
    import cPickle as pickle
except ImportError:
    import pickle

# django
from django.core import signing
from django.utils import timezone

# local
from .conf import Conf, redis_client, logger
from .models import Schedule, Task
from .humanhash import uuid


def async(func, *args, **kwargs):
    """
    Sends a task to the cluster
    """

    hook = kwargs.pop('hook', None)
    list_key = kwargs.pop('list_key', Conf.Q_LIST)
    r = kwargs.pop('redis', redis_client)
    tag = uuid()
    task = {'id': tag[1], 'name': tag[0], 'func': func, 'hook': hook, 'args': args, 'kwargs': kwargs,
            'started': timezone.now()}
    pack = SignedPackage.dumps(task)
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


class SignedPackage(object):
    """
    Wraps Django's signing module with custom Pickle serializer
    """

    @staticmethod
    def dumps(obj, compressed=Conf.COMPRESSED):
        return signing.dumps(obj,
                             key=Conf.SECRET_KEY,
                             salt='django_q.q',
                             compress=compressed,
                             serializer=PickleSerializer)

    @staticmethod
    def loads(obj):
        return signing.loads(obj,
                             key=Conf.SECRET_KEY,
                             salt='django_q.q',
                             serializer=PickleSerializer)


class PickleSerializer(object):
    """
    Simple wrapper around Pickle for signing.dumps and
    signing.loads.
    """

    @staticmethod
    def dumps(obj):
        return pickle.dumps(obj)

    @staticmethod
    def loads(data):
        return pickle.loads(data)
