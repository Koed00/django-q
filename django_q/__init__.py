import os
import sys
from django import get_version

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)

VERSION = (0, 8, 0)

default_app_config = 'django_q.apps.DjangoQConfig'

# root imports will slowly be deprecated.
# please import from the relevant sub modules
split_version = get_version().split('.')
if split_version[1] not in ('9', '10', '11'):
    from .tasks import async, schedule, result, result_group, fetch, fetch_group, count_group, delete_group, queue_size
    from .models import Task, Schedule, Success, Failure
    from .cluster import Cluster
    from .status import Stat
    from .brokers import get_broker

__all__ = ['conf', 'cluster', 'models', 'tasks']
