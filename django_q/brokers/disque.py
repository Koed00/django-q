import redis
from django_q.brokers import Broker
from django_q.conf import Conf


class Disque(Broker):
    def enqueue(self, task):
        return self.connection.execute_command(
            'ADDJOB {} {} 500 RETRY {}'.format(self.list_key, task, Conf.RETRY)).decode()

    def dequeue(self):
        task = self.connection.execute_command('GETJOB TIMEOUT 1000 FROM {}'.format(self.list_key))
        if task:
            return task[0][1].decode(), task[0][2].decode()

    def queue_size(self):
        return self.connection.execute_command('QLEN {}'.format(self.list_key))

    def acknowledge(self, ack_id):
        return self.connection.execute_command('ACKJOB {}'.format(ack_id))

    def ping(self):
        return self.connection.ping()

    def delete_queue(self, list_key=None):
        raise NotImplementedError

    @staticmethod
    def get_connection():
        for node in Conf.DISQUE:
            host, port = node.split(':')
            redis_client = redis.Redis(host, int(port))
            try:
                redis_client.ping()
                redis_client.decode_responses = True
                return redis_client
            except redis.exceptions.ConnectionError:
                pass
        raise ConnectionError('Could not connect to any Disque nodes')
