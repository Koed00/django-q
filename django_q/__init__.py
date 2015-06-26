from django_q.models import Task, Schedule
from django_q.core import async

default_app_config = 'django_q.apps.DjangoQConfig'


def result(name):
    """
    Returns the result of the named task
    :type name: str or unicode
    :param name: the task name
    :return: the result object of this task
    :rtype: object or str
    """
    return Task.get_result(name)


def get_task(name):
    """
    Returns the processed task
    :param name: the task name
    :type name: str or unicode
    :return: the full task object
    :rtype: Task
    """
    if Task.objects.filter(name=name).exists():
        return Task.objects.get(name=name)
