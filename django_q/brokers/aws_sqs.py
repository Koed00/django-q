import os
from django_q.conf import Conf
from django_q.brokers import Broker
import boto.sqs
from boto.sqs.message import Message


class Sqs(Broker):
    def __init__(self, list_key=Conf.PREFIX):
        super(Sqs, self).__init__(list_key)
        self.queue = self.get_queue()

    def enqueue(self, task):
        m = Message()
        m.set_body(task)
        self.queue.write(m)
        return m.id

    def dequeue(self):
        rs = self.queue.get_messages(visibility_timeout=Conf.RETRY or 30)
        if rs:
            m = rs[0]
            return m.receipt_handle, m.get_body()

    def acknowledge(self, task_id):
        return self.delete(task_id)

    def queue_size(self):
        return self.queue.count()

    def delete(self, task_id):
        m = Message()
        m.receipt_handle = task_id
        return self.queue.delete_message(m)

    def delete_queue(self):
        self.connection.delete_queue(self.queue)

    def purge_queue(self):
        self.queue.purge()

    def ping(self):
        try:
            self.connection.get_all_queues()
            return True
        except Exception as e:
            raise e

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        conn = boto.sqs.connect_to_region(Conf.SQS['region'],
                                          aws_access_key_id=Conf.SQS['aws_access_key_id'],
                                          aws_secret_access_key=Conf.SQS['aws_secret_access_key'])
        return conn

    def get_queue(self):
        return self.connection.create_queue(self.list_key)
