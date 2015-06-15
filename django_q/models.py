from django.db import models
import socket
from django.utils.translation import ugettext_lazy as _



class Worker(models.Model):
    WORKER = 'W'
    PUBLISHER = 'P'
    QUEUE = 'Q'
    TYPE = (
        (WORKER, _('Worker')),
        (PUBLISHER, _('Publisher')),
        (QUEUE, _('Queue')),
    )
    worker_type = models.CharField(max_length=1, choices=TYPE, default=TYPE[0][0], verbose_name=_('Worker Type'))
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    port = models.PositiveSmallIntegerField()

    @staticmethod
    def get_queue():
        return Worker.objects.filter(worker_type=Worker.QUEUE)
