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
    Conf.DISQUE_NODES = ['127.0.0.1:7711']
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
    task_id = broker.enqueue('test')
    broker.fail(task_id)
    # bulk test
    for i in range(5):
        broker.enqueue('test')
    Conf.BULK = 5
    for i in range(5):
        task = broker.dequeue()
        assert task is not None
        broker.acknowledge(task[0])
    # delete queue
    broker.enqueue('test')
    broker.enqueue('test')
    broker.delete_queue()
    assert broker.queue_size() == 0
    # back to django-redis
    Conf.DISQUE_NODES = None


@pytest.mark.skipif(not os.getenv('IRON_MQ_TOKEN'),
                    reason="requires IronMQ credentials")
def test_ironmq():
    Conf.IRON_MQ = {'host': os.getenv('IRON_MQ_HOST'),
                    'token': os.getenv('IRON_MQ_TOKEN'),
                    'project_id': os.getenv('IRON_MQ_PROJECT_ID')}
    # check broker
    broker = get_broker(list_key='djangoQ')
    assert broker.ping() is True
    assert broker.info() is not None
    # clear before we start
    broker.purge_queue()
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
    assert broker.dequeue() is not None
    sleep(1.5)
    task = broker.dequeue()
    assert len(task) > 0
    broker.acknowledge(task[0])
    sleep(1.5)
    # delete job
    task_id = broker.enqueue('test')
    broker.delete(task_id)
    assert broker.queue_size() == 0
    # fail
    task_id = broker.enqueue('test')
    broker.fail(task_id)
    # bulk test
    for i in range(5):
        broker.enqueue('test')
    Conf.BULK = 5
    for i in range(5):
        task = broker.dequeue()
        assert task is not None
        broker.acknowledge(task[0])
    # delete queue
    broker.enqueue('test')
    broker.enqueue('test')
    broker.purge_queue()
    assert broker.queue_size() == 0
    broker.delete_queue()
    # back to django-redis
    Conf.IRON_MQ = None
    Conf.DJANGO_REDIS = 'default'
