from django_q.conf import Conf
from django.core.cache import caches, InvalidCacheBackendError


class Broker(object):
    def __init__(self, list_key=Conf.Q_LIST):
        self.connection = self.get_connection()
        self.list_key = list_key
        self.cache = self.get_cache()

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

    def set_stat(self, key, value, timeout):
        key_list = self.cache.get(Conf.Q_STAT, [])
        if key not in key_list:
            key_list.append(key)
        self.cache.set(Conf.Q_STAT, key_list)
        return self.cache.set(key, value, timeout)

    def get_stat(self, key):
        return self.cache.get(key)

    def get_stats(self, pattern):
        key_list = self.cache.get(Conf.Q_STAT)
        if not key_list or len(key_list) == 0:
            return []
        stats = []
        for key in key_list:
            stat = self.cache.get(key)
            if stat:
                stats.append(stat)
            else:
                key_list.remove(key)
        self.cache.set(Conf.Q_STAT, key_list)
        return stats

    @staticmethod
    def get_cache():
        try:
            return caches[Conf.CACHE]
        except InvalidCacheBackendError:
            return None

    @staticmethod
    def get_connection():
        return 0


def get_broker(list_key=Conf.Q_LIST):
    if Conf.DJANGO_REDIS:
        from brokers import djangoredis
        return djangoredis.DjangoRedis(list_key=list_key)
    elif Conf.DISQUE:
        from brokers import disque
        return disque.Disque(list_key=list_key)
    # default to redis
    else:
        from brokers import redis
        return redis.Redis(list_key=list_key)
