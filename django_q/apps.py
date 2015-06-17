from django.apps import AppConfig
from django.conf import settings


class SessionAdminConfig(AppConfig):
    name = 'django_q'
    verbose_name = "Django Q"

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
