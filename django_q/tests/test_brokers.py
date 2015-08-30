from time import sleep
import pytest
from django_q.conf import Conf
from django_q.brokers import get_broker, Broker


def test_broker():
    broker = Broker()
    broker.enqueue('test')
    broker.dequeue()
    broker.queue_size()
    broker.delete_queue()
    broker.acknowledge('test')
    broker.ping()
    assert broker.get_stat('test_1') is None
    broker.set_stat('test_1', 'test', 3)
    assert broker.get_stat('test_1') == 'test'
    assert broker.get_stats('test:*')[0] == 'test'


def test_redis():
    Conf.DJANGO_REDIS = None
    broker = get_broker()
    assert broker.ping() is True
    Conf.REDIS = {'host': '127.0.0.1', 'port': 7712}
    broker = get_broker()
    with pytest.raises(Exception):
        broker.ping()
    Conf.REDIS = None
    Conf.DJANGO_REDIS = 'default'


def test_disque():
    Conf.DISQUE = ['127.0.0.1:7711']
    broker = get_broker()
    assert broker.ping() is True
    broker.enqueue('test')
    assert broker.queue_size() == 1
    task = broker.dequeue()
    assert task[1] == 'test'
    broker.acknowledge(task[0])
    assert broker.queue_size() == 0
    # Retry test
    Conf.RETRY = 1
    broker.enqueue('test')
    assert broker.queue_size() == 1
    broker.dequeue()
    assert broker.queue_size() == 0
    sleep(1.5)
    assert broker.queue_size() == 1
    task = broker.dequeue()
    assert broker.queue_size() == 0
    broker.acknowledge(task[0])
    sleep(1.5)
    assert broker.queue_size() == 0
    # errors
    with pytest.raises(NotImplementedError):
        broker.delete_queue()
    Conf.DISQUE = ['127.0.0.1:7712', '127.0.0.1:7713']
    with pytest.raises(ConnectionError):
        broker.get_connection()
    # back to django-redis
    Conf.DISQUE = None
    Conf.DJANGO_REDIS = 'default'
