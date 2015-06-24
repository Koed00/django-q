import importlib
import logging

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from picklefield import PickledObjectField


class Task(models.Model):
    name = models.CharField(max_length=100)
    func = models.CharField(max_length=256)
    hook = models.CharField(max_length=256, null=True)
    args = PickledObjectField()
    kwargs = PickledObjectField()
    result = PickledObjectField()
    started = models.DateTimeField()
    stopped = models.DateTimeField()
    success = models.BooleanField(default=True)

    @staticmethod
    def get_result(name):
        if Task.objects.filter(name=name).exists():
            return Task.objects.get(name=name).result
        return None

    def time_taken(self):
        return (self.stopped - self.started).total_seconds()

    class Meta:
        app_label = 'django_q'

@receiver(pre_save, sender=Task)
def call_hook(sender, instance, **kwargs):
    if instance.hook:
        module, func = instance.hook.rsplit('.', 1)
        try:
            m = importlib.import_module(module)
            f = getattr(m, func)
            f(instance)
        except Exception as e:
            logger = logging.getLogger('django-q')
            logger.error('return hook failed on {}'.format(instance.name))
            logger.exception(e)


class SuccessManager(models.Manager):
    def get_queryset(self):
        return super(SuccessManager, self).get_queryset().filter(
            success=True)


class Success(Task):
    objects = SuccessManager()

    class Meta:
        app_label = 'django_q'
        verbose_name = 'Successful task'
        proxy = True


class FailureManager(models.Manager):
    def get_queryset(self):
        return super(FailureManager, self).get_queryset().filter(
            success=False)


class Failure(Task):
    objects = FailureManager()

    class Meta:
        app_label = 'django_q'
        verbose_name = 'Failed task'
        proxy = True
