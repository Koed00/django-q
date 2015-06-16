from django.db import models
import socket
from django.utils.translation import ugettext_lazy as _


class Task(models.Model):
    name = models.CharField(max_length=100)
    func = models.CharField(max_length=256)
    task = models.TextField(null=True)
    result = models.TextField(null=True)
    started = models.DateTimeField()
    stopped = models.DateTimeField()
    success = models.BooleanField(default=True)

    def time_taken(self):
        return (self.stopped - self.started).total_seconds()

    class Meta:
        app_label = 'django_q'
