from django_q.conf import Conf
from django_q.brokers import Broker
from iron_mq import IronMQ


class IronMQBroker(Broker):

    def enqueue(self, task):
        return self.connection.post(task)['ids'][0]

    def dequeue(self):
        timeout = Conf.RETRY or None
        task = self.connection.get(timeout=timeout, wait=1)['messages']
        if task:
            return task[0]['id'], task[0]['body']

    def ping(self):
        return self.connection.name == self.list_key

    def queue_size(self):
        return self.connection.size()

    def delete_queue(self):
        return self.connection.delete_queue()['msg']

    def purge_queue(self):
        return self.connection.clear()['msg']

    def delete(self, task_id):
        return self.connection.delete(task_id)['msg']

    def acknowledge(self, task_id):
        return self.delete(task_id)

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        ironmq = IronMQ(name=None, **Conf.IRONMQ)
        return ironmq.queue(queue_name=list_key)
