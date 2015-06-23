import sys
import os
from time import sleep
from multiprocessing import Queue, Event

import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from django_q.core import Cluster, r, async, Q_LIST, pusher, worker, monitor
from django_q.humanhash import DEFAULT_WORDLIST
from django_q import result


class WordClass(object):
    def __init__(self):
        self.word_list = DEFAULT_WORDLIST

    def get_words(self):
        return self.word_list


def test_admin_view(admin_client):
    response = admin_client.get('/admin/django_q/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/failure/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/success/')
    assert response.status_code == 200


def test_redis_connection():
    assert r.ping() is True


def test_cluster_initial():
    c = Cluster()
    assert c.sentinel is None
    assert c.is_idle
    c.start()
    while c.is_starting:
        sleep(0.2)
    assert c.sentinel.is_alive() is True
    assert c.is_running
    c.stop()
    while c.is_stopping:
        sleep(0.2)
    assert c.sentinel.is_alive() is False
    assert c.has_stopped


@pytest.mark.django_db
def test_cluster():
    task = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST)
    task_count = r.llen(Q_LIST)
    assert task_count >= 1
    task_queue = Queue()
    assert task_queue.qsize() == 0
    result_queue = Queue()
    assert result_queue.qsize() == 0
    event = Event()
    event.set()
    # Test push
    pusher(task_queue, event)
    assert task_queue.qsize() == 1
    assert r.llen(Q_LIST) == task_count - 1
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


@pytest.mark.django_db
def test_async():
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, hook='django_q.tests.test_q.assert_result')
    b = async('django_q.tests.tasks.count_letters2', WordClass(), hook='django_q.tests.test_q.assert_result')
    c = Cluster()
    assert c.start() > 0
    while not c.is_running:
        sleep(0.5)
    assert isinstance(a, str)
    assert isinstance(b, str)
    while c.stat.task_q_size > 0 and c.stat.done_q_size > 0:
        sleep(0.5)
    assert c.stop() is True
    result_a = result(a)
    assert result_a is not None
    assert result_a.success is True
    assert result_a.result == 1506
    result_b = result(b)
    assert result_b is not None
    assert result_b.success is True
    assert result_b.result == 1506



@pytest.mark.django_db
def assert_result(task):
    assert task is not None
    assert task.success is True
    assert task.result == 1506


@pytest.mark.django_db
def broken_package():
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, 'oneargumentoomany',
              hook='django_q.tests.test_q.assert_bad_result')
    b = async('django_q.tests.tasks.does_not_exist', WordClass(), hook='django_q.tests.test_q.assert_bad_result')
    assert isinstance(a, str)
    assert isinstance(b, str)
    sleep(5)
    result_a = result(a)
    assert result_a.success is False
    result_b = result(b)
    assert result_b.success is False


@pytest.mark.django_db
def assert_bad_result(task):
    assert task is not None
    assert task.success is False
