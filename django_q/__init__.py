from django_q.models import Task
from django_q.core import async, Cluster

default_app_config = 'django_q.apps.DjangoQConfig'

def result(name):
    return Task.get_result(name)