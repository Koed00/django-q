import sys
from multiprocessing import Queue, Event, Value
import threading

import os
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from django_q.cluster import Cluster, Sentinel, pusher, worker, monitor
from django_q.humanhash import DEFAULT_WORDLIST
from django_q.tasks import fetch, fetch_group, async, result, result_group
from django_q.models import Task
from django_q.conf import Conf, redis_client
from .tasks import multiply


class WordClass(object):
    def __init__(self):
        self.word_list = DEFAULT_WORDLIST

    def get_words(self):
        return self.word_list


@pytest.fixture
def r():
    return redis_client


def test_redis_connection(r):
    assert r.ping() is True


@pytest.mark.django_db
def test_sync(r):
    task = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, redis=r, sync=True)
    assert result(task) == 1506


@pytest.mark.django_db
def test_cluster_initial(r):
    list_key = 'initial_test:q'
    r.delete(list_key)
    c = Cluster(list_key=list_key)
    assert c.sentinel is None
    assert c.stat.status == Conf.STOPPED
    assert c.start() > 0
    assert c.sentinel.is_alive() is True
    assert c.is_running
    assert c.is_stopping is False
    assert c.is_starting is False
    stat = c.stat
    assert stat.status == Conf.IDLE
    assert c.stop() is True
    assert c.sentinel.is_alive() is False
    assert c.has_stopped
    r.delete(list_key)


@pytest.mark.django_db
def test_sentinel():
    start_event = Event()
    stop_event = Event()
    stop_event.set()
    s = Sentinel(stop_event, start_event, list_key='sentinel_test:q')
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED


@pytest.mark.django_db
def test_cluster(r):
    list_key = 'cluster_test:q'
    r.delete(list_key)
    task = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, list_key=list_key)
    assert r.llen(list_key) == 1
    task_queue = Queue()
    assert task_queue.qsize() == 0
    result_queue = Queue()
    assert result_queue.qsize() == 0
    event = Event()
    event.set()
    # Test push
    pusher(task_queue, event, list_key=list_key, r=r)
    assert task_queue.qsize() == 1
    assert r.llen(list_key) == 0
    # Test work
    task_queue.put('STOP')
    worker(task_queue, result_queue, Value('b', -1))
    assert task_queue.qsize() == 0
    assert result_queue.qsize() == 1
    # Test monitor
    result_queue.put('STOP')
    monitor(result_queue)
    assert result_queue.qsize() == 0
    # check result
    assert result(task) == 1506
    r.delete(list_key)


@pytest.mark.django_db
def test_async(r, admin_user):
    list_key = 'cluster_test:q'
    r.delete(list_key)
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, hook='django_q.tests.test_cluster.assert_result',
              list_key=list_key, redis=r)
    b = async('django_q.tests.tasks.count_letters2', WordClass(), hook='django_q.tests.test_cluster.assert_result',
              list_key=list_key, redis=r)
    # unknown argument
    c = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, 'oneargumentoomany',
              hook='django_q.tests.test_cluster.assert_bad_result', list_key=list_key, redis=r)
    # unknown function
    d = async('django_q.tests.tasks.does_not_exist', WordClass(), hook='django_q.tests.test_cluster.assert_bad_result',
              list_key=list_key, redis=r)
    # function without result
    e = async('django_q.tests.tasks.countdown', 100000, list_key=list_key, redis=r)
    # function as instance
    f = async(multiply, 753, 2, hook=assert_result, list_key=list_key, redis=r)
    # model as argument
    g = async('django_q.tests.tasks.get_task_name', Task(name='John'), list_key=list_key, redis=r)
    # args,kwargs, group and broken hook
    h = async('django_q.tests.tasks.word_multiply', 2, word='django', hook='fail.me', list_key=list_key, redis=r)
    # args unpickle test
    j = async('django_q.tests.tasks.get_user_id', admin_user, list_key=list_key, group='test_j', redis=r)
    # check if everything has a task id
    assert isinstance(a, str)
    assert isinstance(b, str)
    assert isinstance(c, str)
    assert isinstance(d, str)
    assert isinstance(e, str)
    assert isinstance(f, str)
    assert isinstance(g, str)
    assert isinstance(h, str)
    assert isinstance(j, str)
    # run the cluster to execute the tasks
    task_count = 9
    assert r.llen(list_key) == task_count
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push the tasks
    for i in range(task_count):
        pusher(task_queue, stop_event, list_key=list_key, r=r)
    assert r.llen(list_key) == 0
    assert task_queue.qsize() == task_count
    task_queue.put('STOP')
    # let a worker handle them
    result_queue = Queue()
    worker(task_queue, result_queue, Value('b', -1))
    assert result_queue.qsize() == task_count
    result_queue.put('STOP')
    # store the results
    monitor(result_queue)
    assert result_queue.qsize() == 0
    # Check the results
    # task a
    result_a = fetch(a)
    assert result_a is not None
    assert result_a.success is True
    assert result(a) == 1506
    # task b
    result_b = fetch(b)
    assert result_b is not None
    assert result_b.success is True
    assert result(b) == 1506
    # task c
    result_c = fetch(c)
    assert result_c is not None
    assert result_c.success is False
    # task d
    result_d = fetch(d)
    assert result_d is not None
    assert result_d.success is False
    # task e
    result_e = fetch(e)
    assert result_e is not None
    assert result_e.success is True
    assert result(e) is None
    # task f
    result_f = fetch(f)
    assert result_f is not None
    assert result_f.success is True
    assert result(f) == 1506
    # task g
    result_g = fetch(g)
    assert result_g is not None
    assert result_g.success is True
    assert result(g) == 'John'
    # task h
    result_h = fetch(h)
    assert result_h is not None
    assert result_h.success is True
    assert result(h) == 12
    # task j
    result_j = fetch(j)
    assert result_j is not None
    assert result_j.success is True
    assert result_j.result == result_j.args[0].id
    assert result_group('test_j') == [result_j.result]
    assert fetch_group('test_j')[0].id == [result_j][0].id
    r.delete(list_key)


@pytest.mark.django_db
def test_timeout(r):
    # set up the Sentinel
    list_key = 'timeout_test:q'
    async('django_q.tests.tasks.count_forever', list_key=list_key)
    start_event = Event()
    stop_event = Event()
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, list_key=list_key, timeout=1)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    r.delete(list_key)


@pytest.mark.django_db
def test_timeout(r):
    # set up the Sentinel
    list_key = 'timeout_test:q'
    async('django_q.tests.tasks.count_forever', list_key=list_key)
    start_event = Event()
    stop_event = Event()
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, list_key=list_key, timeout=1)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    r.delete(list_key)


@pytest.mark.django_db
def test_timeout_override(r):
    # set up the Sentinel
    list_key = 'timeout_override_test:q'
    async('django_q.tests.tasks.count_forever', list_key=list_key, timeout=1)
    start_event = Event()
    stop_event = Event()
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, list_key=list_key, timeout=10)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    r.delete(list_key)


@pytest.mark.django_db
def test_recycle(r):
    # set up the Sentinel
    list_key = 'test_recycle_test:q'
    async('django_q.tests.tasks.multiply', 2, 2, list_key=list_key)
    async('django_q.tests.tasks.multiply', 2, 2, list_key=list_key)
    async('django_q.tests.tasks.multiply', 2, 2, list_key=list_key)
    start_event = Event()
    stop_event = Event()
    # override settings
    Conf.RECYCLE = 2
    Conf.WORKERS = 1
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, list_key=list_key)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    r.delete(list_key)


@pytest.mark.django_db
def assert_result(task):
    assert task is not None
    assert task.success is True
    assert task.result == 1506


@pytest.mark.django_db
def assert_bad_result(task):
    assert task is not None
    assert task.success is False
