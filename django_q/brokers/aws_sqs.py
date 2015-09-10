from django_q.conf import Conf
from django_q.brokers import Broker
from boto3 import Session


class Sqs(Broker):
    def __init__(self, list_key=Conf.PREFIX):
        self.sqs = None
        super(Sqs, self).__init__(list_key)
        self.queue = self.get_queue()

    def enqueue(self, task):
        response = self.queue.send_message(MessageBody=task)
        return response.get('MessageId')

    def dequeue(self):
        # sqs supports max 10 messages in bulk
        if Conf.BULK > 10:
            Conf.BULK = 10
        t = None
        if len(self.task_cache) > 0:
            t = self.task_cache.pop()
        else:
            tasks = self.queue.receive_messages(MaxNumberOfMessages=Conf.BULK, VisibilityTimeout=Conf.RETRY)
            if tasks:
                t = tasks.pop()
                if tasks:
                    self.task_cache = tasks
        if t:
            return t.receipt_handle, t.body

    def acknowledge(self, task_id):
        return self.delete(task_id)

    def queue_size(self):
        return int(self.queue.attributes['ApproximateNumberOfMessages'])

    def delete(self, task_id):
        message = self.sqs.Message(self.queue.url, task_id)
        message.delete()

    def fail(self, task_id):
        self.delete(task_id)

    def delete_queue(self):
        self.queue.delete()

    def purge_queue(self):
        self.queue.purge()

    def ping(self):
        return 'sqs' in self.connection.get_available_resources()

    def info(self):
        return 'AWS SQS'

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        return Session(aws_access_key_id=Conf.SQS['aws_access_key_id'],
                       aws_secret_access_key=Conf.SQS['aws_secret_access_key'],
                       region_name=Conf.SQS['aws_region'])

    def get_queue(self):
        self.sqs = self.connection.resource('sqs')
        return self.sqs.create_queue(QueueName=self.list_key)
