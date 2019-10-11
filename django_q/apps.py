from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import transaction
from django.utils.module_loading import autodiscover_modules

from django_q.conf import Conf, logger
from django_q.registry import registry


def load_registered_schedules(*args, **kwargs):

    from django_q.models import Schedule

    logger.debug("autodiscovering schedules.py...")
    autodiscover_modules("schedules")

    logger.info('the following schedules have been registered : {}'.format(', '.join(registry.keys())))

    with transaction.atomic():
        logger.debug("deleting schedules that were previously added from the registry")
        Schedule.objects.filter(from_registry=True).delete()

        for task_name, kwargs_ in registry.items():
            logger.debug("adding schedule {}".format(task_name))
            Schedule.objects.create(
                **kwargs_
            )

class DjangoQConfig(AppConfig):
    name = 'django_q'
    verbose_name = Conf.LABEL

    def ready(self):
        post_migrate.connect(load_registered_schedules, sender=self)
        from django_q.signals import call_hook
