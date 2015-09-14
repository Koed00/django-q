import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)

from .tasks import async, schedule, result, result_group, fetch, fetch_group, count_group, delete_group, queue_size
from .models import Task, Schedule, Success, Failure
from .cluster import Cluster
from .status import Stat

VERSION = (0, 7, 0)

default_app_config = 'django_q.apps.DjangoQConfig'
