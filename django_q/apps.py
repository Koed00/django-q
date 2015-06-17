from django.apps import AppConfig
from django.conf import settings


class SessionAdminConfig(AppConfig):
    name = 'django_q'
    verbose_name = "Django Q"


try:
    LOG_LEVEL = settings.Q_LOG_LEVEL
except AttributeError:
    LOG_LEVEL = "INFO"

try:
    SECRET_KEY = settings.SECRET_KEY
except AttributeError:
    SECRET_KEY = 'omgicantbelieveyoudonthaveasecretkey'

