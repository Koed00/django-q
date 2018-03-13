# import os
# import sys
import django

# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath)

VERSION = (0, 9, 4)

default_app_config = 'django_q.apps.DjangoQConfig'

# root imports will slowly be deprecated.
# please import from the relevant sub modules
if django.VERSION[:2] < (1, 9):
    from .tasks import async, schedule, result, result_group, fetch, fetch_group, count_group, delete_group, queue_size
    from .models import Task, Schedule, Success, Failure
    from .cluster import Cluster
    from .status import Stat
    from .brokers import get_broker

__all__ = ['conf', 'cluster', 'models', 'tasks']
