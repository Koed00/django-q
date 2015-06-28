from django.apps import AppConfig
from .conf import LABEL


class DjangoQConfig(AppConfig):
    name = 'django_q'
    verbose_name = LABEL
