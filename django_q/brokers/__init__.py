from django_q.conf import Conf


class Broker(object):
    def __init__(self, list_key=Conf.Q_LIST):
        self.connection = self.get_connection()
        self.list_key = list_key

    def enqueue(self, task):
        pass

    def dequeue(self):
        pass

    def queue_size(self):
        pass

    def delete_queue(self, list_key=None):
        pass

    def acknowledge(self, ack_id):
        pass

    def ping(self):
        pass

    def set(self, key, value, timeout):
        pass

    def get(self, key):
        pass

    def get_pattern(self, pattern):
        pass

    @staticmethod
    def get_connection():
        return 0


def get_broker(list_key=Conf.Q_LIST):
    if Conf.REDIS:
        from brokers import redis
        return redis.Redis(list_key=list_key)
    elif Conf.DJANGO_REDIS:
        from brokers import django_redis
        return django_redis.DjangoRedis(list_key=list_key)
