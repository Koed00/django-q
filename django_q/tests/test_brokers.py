from time import sleep
import pytest
import os
import redis
from django_q.conf import Conf
from django_q.brokers import get_broker, Broker


def test_broker():
    broker = Broker()
    broker.enqueue('test')
    broker.dequeue()
    broker.queue_size()
    broker.purge_queue()
    broker.delete('id')
    broker.delete_queue()
    broker.acknowledge('test')
    broker.ping()
    broker.info()
    assert broker.get_stat('test_1') is None
    broker.set_stat('test_1', 'test', 3)
    assert broker.get_stat('test_1') == 'test'
    assert broker.get_stats('test:*')[0] == 'test'


def test_redis():
    Conf.DJANGO_REDIS = None
    broker = get_broker()
    assert broker.ping() is True
    assert broker.info() is not None
    Conf.REDIS = {'host': '127.0.0.1', 'port': 7712}
    broker = get_broker()
    with pytest.raises(Exception):
        broker.ping()
    Conf.REDIS = None
    Conf.DJANGO_REDIS = 'default'


def test_disque():
    # Either local disque or Heroku Tynd
    Conf.DISQUE_NODES = os.getenv('TYND_DISQUE_NODES', '127.0.0.1:7711').split(',')
    if os.getenv('TYND_DISQUE_AUTH', False):
        Conf.DISQUE_AUTH = os.environ['TYND_DISQUE_AUTH']
    # check broker
    broker = get_broker(list_key='disque_test')
    assert broker.ping() is True
    assert broker.info() is not None
    # clear before we start
    broker.delete_queue()
    # enqueue
    broker.enqueue('test')
    assert broker.queue_size() == 1
    # dequeue
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
    # connection test
    Conf.DISQUE_NODES = ['127.0.0.1:7712', '127.0.0.1:7713']
    with pytest.raises(redis.exceptions.ConnectionError):
        broker.get_connection()
    # delete job
    task_id = broker.enqueue('test')
    broker.delete(task_id)
    assert broker.queue_size() == 0
    # fail
    task_id=broker.enqueue('test')
    broker.fail(task_id)
    # delete queue
    broker.enqueue('test')
    broker.enqueue('test')
    broker.delete_queue()
    assert broker.queue_size() == 0
    # back to django-redis
    Conf.DISQUE_NODES = None
