import sys
import os
from time import sleep
from multiprocessing import Queue, Event

import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from django_q.core import Cluster, r, async, pusher, worker, monitor, Sentinel
from django_q.humanhash import DEFAULT_WORDLIST
from django_q import result, get_task
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
    c.start()
    assert c.sentinel.is_alive() is True
    assert c.is_running
    c.stop()
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
def run_cluster():
    list_key = 'run_test:q'
    r.delete(list_key)
    c = Cluster(list_key=list_key)
    assert c.start() > 0
    while c.stat.task_q_size > 0 and c.stat.done_q_size > 0:
        sleep(0.5)
    assert c.stop() is True
    r.delete(list_key)


@pytest.mark.django_db
def blah_async():
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, hook='django_q.tests.test_q.assert_result')
    b = async('django_q.tests.tasks.count_letters2', WordClass(), hook='django_q.tests.test_q.assert_result')
    # unknown argument
    c = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, 'oneargumentoomany',
              hook='django_q.tests.test_q.assert_bad_result')
    # unknown function
    d = async('django_q.tests.tasks.does_not_exist', WordClass(), hook='django_q.tests.test_q.assert_bad_result')
    # function without result
    e = async('django_q.tests.tasks.countdown', 100000)
    # function as instance
    f = async(multiply, 753, 2, hook=assert_result)
    # check if everything has a task name
    assert isinstance(a, str)
    assert isinstance(b, str)
    assert isinstance(c, str)
    assert isinstance(d, str)
    assert isinstance(e, str)
    assert isinstance(f, str)
    # run the cluster to execute the tasks
    run_cluster()
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
