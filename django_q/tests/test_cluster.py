import sys
import os
from multiprocessing import Queue, Event

import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from django_q.core import Cluster, r, async, pusher, worker, monitor, Sentinel
from django_q.humanhash import DEFAULT_WORDLIST
from django_q import result, get_task, Task
from django_q.tests.tasks import multiply


class WordClass(object):
    def __init__(self):
        self.word_list = DEFAULT_WORDLIST

    def get_words(self):
        return self.word_list


def test_redis_connection():
    assert r.ping() is True


def test_cluster_initial():
    c = Cluster()
    assert c.sentinel is None
    assert c.is_idle
    assert c.start() > 0
    assert c.sentinel.is_alive() is True
    assert c.is_running
    assert c.stop() is True
    assert c.sentinel.is_alive() is False
    assert c.has_stopped


def test_sentinel():
    start_event = Event()
    stop_event = Event()
    stop_event.set()
    Sentinel(stop_event, start_event, list_key='sentinel_test:q')
    assert start_event.is_set()


@pytest.mark.django_db
def test_cluster():
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
    pusher(task_queue, event, list_key=list_key)
    assert task_queue.qsize() == 1
    assert r.llen(list_key) == 0
    # Test work
    task_queue.put('STOP')
    worker(task_queue, result_queue)
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
def test_async():
    list_key = 'cluster_test:q'
    r.delete(list_key)
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, hook='django_q.tests.test_cluster.assert_result',
              list_key=list_key)
    b = async('django_q.tests.tasks.count_letters2', WordClass(), hook='django_q.tests.test_cluster.assert_result',
              list_key=list_key)
    # unknown argument
    c = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, 'oneargumentoomany',
              hook='django_q.tests.test_cluster.assert_bad_result', list_key=list_key)
    # unknown function
    d = async('django_q.tests.tasks.does_not_exist', WordClass(), hook='django_q.tests.test_cluster.assert_bad_result',
              list_key=list_key)
    # function without result
    e = async('django_q.tests.tasks.countdown', 100000, list_key=list_key)
    # function as instance
    f = async(multiply, 753, 2, hook=assert_result, list_key=list_key)
    # model as argument
    g = async('django_q.tests.tasks.get_task_name', Task(name='John'), list_key=list_key)
    # check if everything has a task name
    assert isinstance(a, str)
    assert isinstance(b, str)
    assert isinstance(c, str)
    assert isinstance(d, str)
    assert isinstance(e, str)
    assert isinstance(f, str)
    assert isinstance(g, str)
    # run the cluster to execute the tasks
    task_count = 7
    assert r.llen(list_key) == task_count
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push the tasks
    for i in range(task_count):
        pusher(task_queue, stop_event, list_key=list_key)
    assert r.llen(list_key) == 0
    assert task_queue.qsize() == task_count
    task_queue.put('STOP')
    # let a worker handle them
    result_queue = Queue()
    worker(task_queue, result_queue)
    assert result_queue.qsize() == task_count
    result_queue.put('STOP')
    # store the results
    monitor(result_queue)
    assert result_queue.qsize() == 0
    # Check the results
    # task a
    result_a = get_task(a)
    assert result_a is not None
    assert result_a.success is True
    assert result(a) == 1506
    # task b
    result_b = get_task(b)
    assert result_b is not None
    assert result_b.success is True
    assert result(b) == 1506
    # task c
    result_c = get_task(c)
    assert result_c is not None
    assert result_c.success is False
    # task d
    result_d = get_task(d)
    assert result_d is not None
    assert result_d.success is False
    # task e
    result_e = get_task(e)
    assert result_e is not None
    assert result_e.success is True
    assert result(e) is None
    # task f
    result_f = get_task(f)
    assert result_f is not None
    assert result_f.success is True
    assert result(f) == 1506
    # task g
    result_g = get_task(g)
    assert result_g is not None
    assert result_g.success is True
    assert result(g) == 'John'
    r.delete(list_key)


# not sure if this actually asserts, but it is called
@pytest.mark.django_db
def assert_result(task):
    assert task is not None
    assert task.success is True
    assert task.result == 1506


@pytest.mark.django_db
def assert_bad_result(task):
    assert task is not None
    assert task.success is False
