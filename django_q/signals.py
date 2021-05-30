import importlib

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils.translation import gettext_lazy as _

from django_q.conf import logger
from django_q.models import Task


@receiver(post_save, sender=Task)
def call_hook(sender, instance, **kwargs):
    if instance.hook:
        f = instance.hook
        if not callable(f):
            try:
                module, func = f.rsplit(".", 1)
                m = importlib.import_module(module)
                f = getattr(m, func)
            except (ValueError, ImportError, AttributeError):
                logger.error(
                    _(f"malformed return hook '{instance.hook}' for [{instance.name}]")
                )
                return
        try:
            f(instance)
        except Exception as e:
            logger.error(
                _(
                    f"return hook {instance.hook} failed on [{instance.name}] because {str(e)}"
                )
            )


# args: task
pre_enqueue = Signal()

# args: func, task
pre_execute = Signal()
