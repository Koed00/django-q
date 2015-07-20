import pytest

from django_q import conf


@pytest.fixture
def r():
    return conf.redis_client


def test_django_redis():
    conf.Conf.DJANGO_REDIS = None
    assert conf.redis_client.ping() is True
    conf.Conf.DJANGO_REDIS = 'default'
    assert conf.redis_client.ping() is True
