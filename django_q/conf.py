import logging
from signal import signal
from multiprocessing import cpu_count, Queue

# django
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# external
import os

# optional
try:
    import psutil
except ImportError:
    psutil = None


class Conf(object):
    """
    Configuration class
    """
    try:
        conf = settings.Q_CLUSTER
    except AttributeError:
        conf = {}

    # Redis server configuration . Follows standard redis keywords
    REDIS = conf.get('redis', {})

    # Support for Django-Redis connections

    DJANGO_REDIS = conf.get('django_redis', None)

    # Disque broker
    DISQUE_NODES = conf.get('disque_nodes', None)

    # Optional Authentication
    DISQUE_AUTH = conf.get('disque_auth', None)

    # Optional Fast acknowledge
    DISQUE_FASTACK = conf.get('disque_fastack', False)

    # IronMQ broker
    IRON_MQ = conf.get('iron_mq', None)

    # SQS broker
    SQS = conf.get('sqs', None)

    # ORM broker
    ORM = conf.get('orm', None)

    # MongoDB broker
    MONGO = conf.get('mongo', None)
    MONGO_DB = conf.get('mongo_db', None)

    # Name of the cluster or site. For when you run multiple sites on one redis server
    PREFIX = conf.get('name', 'default')

    # Log output level
    LOG_LEVEL = conf.get('log_level', 'INFO')

    # Maximum number of successful tasks kept in the database. 0 saves everything. -1 saves none
    # Failures are always saved
    SAVE_LIMIT = conf.get('save_limit', 250)

    # Disable the scheduler
    SCHEDULER = conf.get('scheduler', True)

    # Number of workers in the pool. Default is cpu count if implemented, otherwise 4.
    WORKERS = conf.get('workers', False)
    if not WORKERS:
        try:
            WORKERS = cpu_count()
            # in rare cases this might fail
        except NotImplementedError:
            # try psutil
            if psutil:
                WORKERS = psutil.cpu_count() or 4
            else:
                # sensible default
                WORKERS = 4

    # Maximum number of tasks that each cluster can work on
    QUEUE_LIMIT = conf.get('queue_limit', int(WORKERS) ** 2)

    # Sets compression of redis packages
    COMPRESSED = conf.get('compress', False)

    # Number of tasks each worker can handle before it gets recycled. Useful for releasing memory
    RECYCLE = conf.get('recycle', 500)

    # Number of seconds to wait for a worker to finish.
    TIMEOUT = conf.get('timeout', None)

    # Number of seconds to wait for acknowledgement before retrying a task
    # Only works with brokers that guarantee delivery. Defaults to 60 seconds.
    RETRY = conf.get('retry', 60)

    # Sets the amount of tasks the cluster will try to pop off the broker.
    # If it supports bulk gets.
    BULK = conf.get('bulk', 1)

    # The Django Admin label for this app
    LABEL = conf.get('label', 'Django Q')

    # Sets the number of processors for each worker, defaults to all.
    CPU_AFFINITY = conf.get('cpu_affinity', 0)

    # Global sync option to for debugging
    SYNC = conf.get('sync', False)

    # The Django cache to use
    CACHE = conf.get('cache', 'default')

    # Use the cache as result backend. Can be 'True' or an integer representing the global cache timeout.
    # i.e 'cached: 60' , will make all results go the cache and expire in 60 seconds.
    CACHED = conf.get('cached', False)

    # If set to False the scheduler won't execute tasks in the past.
    # Instead it will run once and reschedule the next run in the future. Defaults to True.
    CATCH_UP = conf.get('catch_up', True)

    # Use the secret key for package signing
    # Django itself should raise an error if it's not configured
    SECRET_KEY = settings.SECRET_KEY

    # The redis stats key
    Q_STAT = 'django_q:{}:cluster'.format(PREFIX)

    # OSX doesn't implement qsize because of missing sem_getvalue()
    try:
        QSIZE = Queue().qsize() == 0
    except NotImplementedError:
        QSIZE = False

    # Getting the signal names
    SIGNAL_NAMES = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    # Translators: Cluster status descriptions
    STARTING = _('Starting')
    WORKING = _('Working')
    IDLE = _("Idle")
    STOPPED = _('Stopped')
    STOPPING = _('Stopping')

    # to manage workarounds during testing
    TESTING = conf.get('testing', False)


# logger
logger = logging.getLogger('django-q')

# Set up standard logging handler in case there is none
if not logger.handlers:
    logger.setLevel(level=getattr(logging, Conf.LOG_LEVEL))
    formatter = logging.Formatter(fmt='%(asctime)s [Q] %(levelname)s %(message)s',
                                  datefmt='%H:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# get parent pid compatibility
def get_ppid():
    if hasattr(os, 'getppid'):
        return os.getppid()
    elif psutil:
        return psutil.Process(os.getpid()).ppid()
    else:
        raise OSError('Your OS does not support `os.getppid`. Please install `psutil` as an alternative provider.')
