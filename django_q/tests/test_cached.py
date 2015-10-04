from multiprocessing import Event

import pytest

from django_q.cluster import Sentinel
from django_q.conf import Conf
from django_q.tasks import async, result, fetch, count_group, result_group, fetch_group, delete_group, delete_cached, \
    async_iter
from django_q.brokers import get_broker


@pytest.fixture
def broker():
    Conf.DISQUE_NODES = None
    Conf.IRON_MQ = None
    Conf.SQS = None
    Conf.ORM = None
    Conf.MONGO = None
    Conf.DJANGO_REDIS = 'default'
    return get_broker()


@pytest.mark.django_db
def test_cached(broker):
    broker.purge_queue()
    broker.cache.clear()
    group = 'cache_test'
    # queue the tests
    task_id = async('math.copysign', 1, -1, cached=True, broker=broker)
    async('math.copysign', 1, -1, cached=True, broker=broker, group=group)
    async('math.copysign', 1, -1, cached=True, broker=broker, group=group)
    async('math.copysign', 1, -1, cached=True, broker=broker, group=group)
    async('math.copysign', 1, -1, cached=True, broker=broker, group=group)
    async('math.copysign', 1, -1, cached=True, broker=broker, group=group)
    async('math.popysign', 1, -1, cached=True, broker=broker, group=group)
    # test wait on cache
    # test wait timeout
    assert result(task_id, wait=10, cached=True) is None
    assert fetch(task_id, wait=10, cached=True) is None
    assert result_group(group, wait=10, cached=True) is None
    assert result_group(group, count=2, wait=10, cached=True) is None
    assert fetch_group(group, wait=10, cached=True) is None
    assert fetch_group(group, count=2, wait=10, cached=True) is None
    # run a single cluster
    start_event = Event()
    stop_event = Event()
    stop_event.set()
    Sentinel(stop_event, start_event, broker=broker)
    # assert results
    assert result(task_id, wait=500, cached=True) == -1
    assert fetch(task_id, wait=500, cached=True).result == -1
    # make sure it's not in the db backend
    assert fetch(task_id) is None
    # assert group
    assert count_group(group, cached=True) == 6
    assert count_group(group, cached=True, failures=True) == 1
    assert result_group(group, cached=True) == [-1, -1, -1, -1, -1]
    assert len(result_group(group, cached=True, failures=True)) == 6
    assert len(fetch_group(group, cached=True)) == 6
    assert len(fetch_group(group, cached=True, failures=False)) == 5
    delete_group(group, cached=True)
    assert count_group(group, cached=True) is None
    delete_cached(task_id)
    assert result(task_id, cached=True) is None
    assert fetch(task_id, cached=True) is None
    broker.cache.clear()


@pytest.mark.django_db
def test_iter(broker):
    broker.purge_queue()
    broker.cache.clear()
    it = [i for i in range(10)]
    it2 = [(1, -1), (2, -1), (3, -4), (5, 6)]
    it3 = (1, 2, 3, 4, 5)
    t = async_iter('math.floor', it, sync=True)
    t2 = async_iter('math.copysign', it2, sync=True)
    t3 = async_iter('math.floor', it3, sync=True)
    t4 = async_iter('math.floor', (1,), sync=True)
    result_t = result(t)
    assert result_t is not None
    task_t = fetch(t)
    assert task_t. __unicode__ is not None
    assert task_t.result == result_t
    assert result(t2) is not None
    assert result(t3) is not None
    assert result(t4)[0] == 1
