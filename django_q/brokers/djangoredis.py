import django_redis
from django_q.brokers import redis_broker
from django_q.conf import Conf


class DjangoRedis(redis_broker.Redis):

    @staticmethod
    def get_connection():
        return django_redis.get_redis_connection(Conf.DJANGO_REDIS)