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


@pytest.mark.skipif(not os.getenv('DISQUE', None),
                    reason="No disque server configured")
def test_disque():
    Conf.DISQUE = ['127.0.0.1:7711']
    broker = get_broker(list_key='disque_test')
    assert broker.ping() is True
    broker.delete_queue()
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
    Conf.DISQUE = ['127.0.0.1:7712', '127.0.0.1:7713']
    with pytest.raises(redis.exceptions.ConnectionError):
        broker.get_connection()
    broker.delete_queue()
    assert broker.queue_size() == 0
    # back to django-redis
    Conf.DISQUE = None


@pytest.mark.skipif(not os.getenv('AWS_ACCESS_KEY_ID'),
                    reason="requires AWS SQS credentials")
def test_sqs():
    Conf.SQS = {'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'region': os.getenv('SQS_REGION', 'eu-west-1')}
    broker = get_broker(list_key='sqs_test')
    assert broker.ping() is True
    if broker.queue_size() > 0:
        broker.purge_queue()
    broker.enqueue('test')
    task = broker.dequeue()
    assert task[1] == 'test'
    broker.acknowledge(task[0])
    assert broker.queue_size() == 0
    # Retry test
    Conf.RETRY = 1
    broker.enqueue('test')
    broker.dequeue()
    assert broker.queue_size() == 0
    sleep(2)
    # task should re-queue
    assert broker.queue_size() == 1
    task = broker.dequeue()
    assert task[1] == 'test'
    assert broker.acknowledge(task[0]) is True
    assert broker.queue_size() == 0
    broker.delete_queue()
    # back to defaults
    Conf.SQS = None


@pytest.mark.skipif(not os.getenv('IRONMQ_TOKEN'),
                    reason="requires IronMQ credentials")
def test_ironmq():
    Conf.IRONMQ = {'host': 'mq-aws-eu-west-1.iron.io',
                   'token': os.getenv('IRONMQ_TOKEN'),
                   'project_id': os.getenv('IRONMQ_PROJECT')}
    broker = get_broker(list_key='djangoQ_test')
    assert broker.ping() is True
    broker.delete_queue()
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
    broker.delete_queue()
    assert broker.queue_size() == 0
    # back to django-redis
    Conf.DISQUE = None
