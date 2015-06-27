from signal import signal
from multiprocessing import cpu_count

from django.conf import settings

VERSION = '0.1.0'

"""
Redis server connection
"""
try:
    REDIS = settings.Q_REDIS
except AttributeError:
    REDIS = {}
"""
Prefixes the Redis keys. Defaults to django_q
"""
try:
    PREFIX = settings.Q_PREFIX
except AttributeError:
    PREFIX = 'django_q'

"""
Sets the logging level for the app
"""
try:
    LOG_LEVEL = settings.Q_LOG_LEVEL
except AttributeError:
    LOG_LEVEL = "INFO"

"""
Using Django's secret key to sign task packages
"""
try:
    SECRET_KEY = settings.SECRET_KEY
except AttributeError:
    SECRET_KEY = 'omgicantbelieveyoudonthaveasecretkey'

"""
SAVE_LIMIT limits the amount of successful task executions saved to the database.
Set this to 0 for no limits.
Failures are not limited.
"""
try:
    SAVE_LIMIT = settings.Q_SAVE_LIMIT
except AttributeError:
    SAVE_LIMIT = 100

try:
    WORKERS = settings.Q_WORKERS
except AttributeError:
    WORKERS = cpu_count()

"""
Turns compression on/off for task packages
"""
try:
    COMPRESSED = settings.Q_COMPRESSED
except AttributeError:
    COMPRESSED = False

try:
    USE_TZ = settings.USE_TZ
except AttributeError:
    USE_TZ = False

"""
Getting the SIGNAL names
"""
SIGNAL_NAMES = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n)

"""
Redis List name
"""
Q_LIST = '{}:q'.format(PREFIX)

"""
Cluster status
"""
STARTING = 'Starting'
RUNNING = 'Running'
STOPPED = 'Stopped'
STOPPING = 'Stopping'
