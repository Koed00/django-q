from django.db import models
from picklefield import PickledObjectField


class Task(models.Model):
    name = models.CharField(max_length=100)
    func = models.CharField(max_length=256)
    args = PickledObjectField()
    kwargs = PickledObjectField()
    result = PickledObjectField()
    started = models.DateTimeField()
    stopped = models.DateTimeField()
    success = models.BooleanField(default=True)

    @staticmethod
    def get_result(name):
        return Task.objects.filter(name=name).values_list('result', flat=True)

    def time_taken(self):
        return (self.stopped - self.started).total_seconds()

    class Meta:
        app_label = 'django_q'


class SuccessManager(models.Manager):
    def get_queryset(self):
        return super(SuccessManager, self).get_queryset().filter(
            success=True)


class Success(Task):
    objects = SuccessManager()

    class Meta:
        app_label = 'django_q'
        proxy = True


class FailureManager(models.Manager):
    def get_queryset(self):
        return super(FailureManager, self).get_queryset().filter(
            success=False)


class Failure(Task):
    objects = FailureManager()

    class Meta:
        app_label = 'django_q'
        proxy = True
