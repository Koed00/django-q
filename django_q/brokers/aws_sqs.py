from django_q.conf import Conf
from django_q.brokers import Broker
import boto.sqs
from boto.sqs.message import RawMessage


class Sqs(Broker):
    def __init__(self, list_key=Conf.PREFIX):
        super(Sqs, self).__init__(list_key)
        self.queue = self.get_queue()

    def enqueue(self, task):
        m = RawMessage()
        m.set_body(task)
        self.queue.write(m)
        return m.id

    def dequeue(self):
        # sqs supports max 10 messages in bulk
        if Conf.BULK > 10:
            Conf.BULK = 10
        t = None
        if len(self.task_cache) > 0:
            t = self.task_cache.pop()
        else:
            tasks = self.queue.get_messages(num_messages=Conf.BULK, visibility_timeout=Conf.RETRY)
            if tasks:
                t = tasks.pop()
                if tasks:
                    self.task_cache = tasks
        if t:
            return t.receipt_handle, t.get_body()

    def acknowledge(self, task_id):
        return self.delete(task_id)

    def queue_size(self):
        return self.queue.count()

    def delete(self, task_id):
        m = RawMessage()
        m.receipt_handle = task_id
        return self.queue.delete_message(m)

    def fail(self, task_id):
        self.delete(task_id)

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

    def info(self):
        return 'AWS SQS'

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        conn = boto.sqs.connect_to_region(Conf.SQS['aws_region'],
                                          aws_access_key_id=Conf.SQS['aws_access_key_id'],
                                          aws_secret_access_key=Conf.SQS['aws_secret_access_key'])
        return conn

    def get_queue(self):
        return self.connection.create_queue(self.list_key)
