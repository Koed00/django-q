from datetime import timedelta
from time import sleep
from django.utils import timezone
from django.db.models import Q
from django_q.brokers import Broker
from django_q.models import OrmQ
from django_q.conf import Conf


class ORM(Broker):
    def queue_size(self):
        return OrmQ.objects.using(Conf.ORM) \
            .filter(Q(key=self.list_key, lock__isnull=True) |
                    Q(key=self.list_key, lock__lte=timezone.now() - timedelta(seconds=Conf.RETRY))) \
            .count()

    def purge_queue(self):
        return OrmQ.objects.using(Conf.ORM).filter(key=self.list_key).delete()

    def ping(self):
        return True

    def info(self):
        return 'ORM {}'.format(Conf.ORM)

    def fail(self, task_id):
        self.delete(task_id)

    def enqueue(self, task):
        package = OrmQ.objects.using(Conf.ORM).create(key=self.list_key, payload=task)
        return package.pk

    def dequeue(self):
            tasks = OrmQ.objects.using(Conf.ORM).filter(
                Q(key=self.list_key, lock__isnull=True) |
                Q(key=self.list_key, lock__lte=timezone.now() - timedelta(seconds=Conf.RETRY)))[:Conf.BULK]
            if tasks:
                # lock them
                OrmQ.objects.using(Conf.ORM).filter(pk__in=tasks).update(lock=timezone.now())
                return [(t.pk, t.payload) for t in tasks]
            # empty queue, spare the cpu
            sleep(0.2)

    def delete_queue(self):
        return self.purge_queue()

    def delete(self, task_id):
        return OrmQ.objects.using(Conf.ORM).filter(pk=task_id).delete()

    def acknowledge(self, task_id):
        return self.delete(task_id)
