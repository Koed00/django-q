from datetime import timedelta
from time import sleep

from django.utils import timezone

from django_q.brokers import Broker
from django_q.models import OrmQ
from django_q.conf import Conf


def _timeout():
    return timezone.now() - timedelta(seconds=Conf.RETRY)


class ORM(Broker):
    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        return OrmQ.objects.using(Conf.ORM)

    def queue_size(self):
        return self.connection.filter(key=self.list_key, lock__lte=_timeout()).count()

    def lock_size(self):
        return self.connection.filter(key=self.list_key, lock__gt=_timeout()).count()

    def purge_queue(self):
        return self.connection.filter(key=self.list_key).delete()

    def ping(self):
        return True

    def info(self):
        if not self._info:
            self._info = 'ORM {}'.format(Conf.ORM)
        return self._info

    def fail(self, task_id):
        self.delete(task_id)

    def enqueue(self, task):
        package = self.connection.create(key=self.list_key, payload=task, lock=_timeout())
        return package.pk

    def dequeue(self):
        tasks = self.connection.filter(key=self.list_key, lock__lt=_timeout())[0:Conf.BULK]
        if tasks:
            task_list = []
            lock = timezone.now()
            for task in tasks:
                task.lock = lock
                task.save(update_fields=['lock'])
                task_list.append((task.pk, task.payload))
            return task_list
        # empty queue, spare the cpu
        sleep(0.2)

    def delete_queue(self):
        return self.purge_queue()

    def delete(self, task_id):
        self.connection.filter(pk=task_id).delete()

    def acknowledge(self, task_id):
        return self.delete(task_id)
