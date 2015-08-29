import pytest

from django_q import conf


def test_django_redis():
    conf.Conf.DJANGO_REDIS = None
    assert conf.redis_client.ping() is True
    conf.Conf.DJANGO_REDIS = 'default'
    assert conf.redis_client.ping() is True
