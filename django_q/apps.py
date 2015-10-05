from django.apps import AppConfig

from .conf import Conf


class DjangoQConfig(AppConfig):
    name = 'django_q'
    verbose_name = Conf.LABEL

    def ready(self):
        from django_q.signals import call_hook