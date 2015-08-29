import redis
from django_q.brokers import Broker
from django_q.conf import Conf, logger


class Redis(Broker):
    def enqueue(self, task):
        return self.connection.rpush(self.list_key, task)

    def dequeue(self):
        task = self.connection.blpop(self.list_key, 1)
        if task:
            return None, task[1]

    def queue_size(self):
        return self.connection.llen(self.list_key)

    def delete_queue(self, list_key=None):
        list_key = list_key if list_key else self.list_key
        return self.connection.delete(list_key)

    def ping(self):
        try:
            return self.connection.ping()
        except Exception as e:
            logger.error('Can not connect to Redis server.')
            raise e

    def set(self, key, value, timeout):
        self.connection.set(key, value, timeout)

    def get(self, key):
        if self.connection.exists(key):
            return self.connection.get(key)

    def get_pattern(self, pattern):
        keys = self.connection.keys(pattern=pattern)
        if keys:
            return self.connection.mget(keys)

    @staticmethod
    def get_connection():
        return redis.StrictRedis(**Conf.REDIS)
