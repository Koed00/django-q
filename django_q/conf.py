from signal import signal
from multiprocessing import cpu_count

from django.conf import settings

VERSION = '0.1.0'

try:
    conf = settings.Q_CLUSTER
except AttributeError:
    conf = {}

# Redis server configuration . Follows standard redis keywords
REDIS = conf.get('redis', {})

# Name of the cluster or site. For when you run multiple sites on one redis server
PREFIX = conf.get('name', 'default')

# Log output level
LOG_LEVEL = conf.get('log_level', 'INFO')

# Maximum number of successful tasks kept in the database. 0 saves everything. -1 saves none
# Failures are always saved
SAVE_LIMIT = conf.get('save_limit', 250)

# Number of workers in the pool. Default is cpu count. +2 for monitor and pusher
WORKERS = conf.get('workers', cpu_count())

# Sets compression of redis packages
COMPRESSED = conf.get('compress', False)

# Number of tasks each worker can handle before it gets recycled. Useful for releasing memory
RECYCLE = conf.get('recycle', 1000)

# The Django Admin label for this app
LABEL = conf.get('label', 'Django Q')

# Use the secret key for package signing
try:
    SECRET_KEY = settings.SECRET_KEY
except AttributeError:
    SECRET_KEY = 'omgicantbelieveudonthaveasecretkey'

# Getting the signal names
SIGNAL_NAMES = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n)

# The redis list key
Q_LIST = 'django_q:{}:q'.format(PREFIX)
# The redis stats key
Q_STAT = 'django_q:{}:cluster'.format(PREFIX)

# Cluster status
STARTING = 'Starting'
RUNNING = 'Running'
STOPPED = 'Stopped'
STOPPING = 'Stopping'
