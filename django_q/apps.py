from django.apps import AppConfig

from .conf import Conf


class DjangoQConfig(AppConfig):
    name = 'django_q'
    verbose_name = Conf.LABEL
