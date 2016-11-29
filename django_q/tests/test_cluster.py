import sys
import threading
from multiprocessing import Queue, Event, Value
from time import sleep
from django.utils import timezone

import os
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from django_q.cluster import Cluster, Sentinel, pusher, worker, monitor, save_task
from django_q.humanhash import DEFAULT_WORDLIST, uuid
from django_q.tasks import fetch, fetch_group, async, result, result_group, count_group, delete_group, queue_size
from django_q.models import Task, Success
from django_q.conf import Conf
from django_q.status import Stat
from django_q.brokers import get_broker
from .tasks import multiply


class WordClass(object):
    def __init__(self):
        self.word_list = DEFAULT_WORDLIST

    def get_words(self):
        return self.word_list


@pytest.fixture
def broker(monkeypatch):
    monkeypatch.setattr(Conf, 'DJANGO_REDIS', 'default')
    return get_broker()


def test_redis_connection(broker):
    assert broker.ping() is True


@pytest.mark.django_db
def test_sync(broker):
    task = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, broker=broker, sync=True)
    assert result(task) == 1506


@pytest.mark.django_db
def test_cluster_initial(broker):
    broker.list_key = 'initial_test:q'
    broker.delete_queue()
    c = Cluster(broker=broker)
    assert c.sentinel is None
    assert c.stat.status == Conf.STOPPED
    assert c.start() > 0
    assert c.sentinel.is_alive() is True
    assert c.is_running
    assert c.is_stopping is False
    assert c.is_starting is False
    sleep(0.5)
    stat = c.stat
    assert stat.status == Conf.IDLE
    assert c.stop() is True
    assert c.sentinel.is_alive() is False
    assert c.has_stopped
    assert c.stop() is False
    broker.delete_queue()


@pytest.mark.django_db
def test_sentinel():
    start_event = Event()
    stop_event = Event()
    stop_event.set()
    s = Sentinel(stop_event, start_event, broker=get_broker('sentinel_test:q'))
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED


@pytest.mark.django_db
def test_cluster(broker):
    broker.list_key = 'cluster_test:q'
    broker.delete_queue()
    task = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, broker=broker)
    assert broker.queue_size() == 1
    task_queue = Queue()
    assert task_queue.qsize() == 0
    result_queue = Queue()
    assert result_queue.qsize() == 0
    event = Event()
    event.set()
    # Test push
    pusher(task_queue, event, broker=broker)
    assert task_queue.qsize() == 1
    assert queue_size(broker=broker) == 0
    # Test work
    task_queue.put('STOP')
    worker(task_queue, result_queue, Value('f', -1))
    assert task_queue.qsize() == 0
    assert result_queue.qsize() == 1
    # Test monitor
    result_queue.put('STOP')
    monitor(result_queue)
    assert result_queue.qsize() == 0
    # check result
    assert result(task) == 1506
    broker.delete_queue()


@pytest.mark.django_db
def test_async(broker, admin_user):
    broker.list_key = 'cluster_test:q'
    broker.delete_queue()
    a = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, hook='django_q.tests.test_cluster.assert_result',
              broker=broker)
    b = async('django_q.tests.tasks.count_letters2', WordClass(), hook='django_q.tests.test_cluster.assert_result',
              broker=broker)
    # unknown argument
    c = async('django_q.tests.tasks.count_letters', DEFAULT_WORDLIST, 'oneargumentoomany',
              hook='django_q.tests.test_cluster.assert_bad_result', broker=broker)
    # unknown function
    d = async('django_q.tests.tasks.does_not_exist', WordClass(), hook='django_q.tests.test_cluster.assert_bad_result',
              broker=broker)
    # function without result
    e = async('django_q.tests.tasks.countdown', 100000, broker=broker)
    # function as instance
    f = async(multiply, 753, 2, hook=assert_result, broker=broker)
    # model as argument
    g = async('django_q.tests.tasks.get_task_name', Task(name='John'), broker=broker)
    # args,kwargs, group and broken hook
    h = async('django_q.tests.tasks.word_multiply', 2, word='django', hook='fail.me', broker=broker)
    # args unpickle test
    j = async('django_q.tests.tasks.get_user_id', admin_user, broker=broker, group='test_j')
    # q_options and save opt_out test
    k = async('django_q.tests.tasks.get_user_id', admin_user,
              q_options={'broker': broker, 'group': 'test_k', 'save': False, 'timeout': 90})
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
    assert isinstance(k, str)
    # run the cluster to execute the tasks
    task_count = 10
    assert broker.queue_size() == task_count
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push the tasks
    for i in range(task_count):
        pusher(task_queue, stop_event, broker=broker)
    assert broker.queue_size() == 0
    assert task_queue.qsize() == task_count
    task_queue.put('STOP')
    # test wait timeout
    assert result(j, wait=10) is None
    assert fetch(j, wait=10) is None
    assert result_group('test_j', wait=10) is None
    assert result_group('test_j', count=2, wait=10) is None
    assert fetch_group('test_j', wait=10) is None
    assert fetch_group('test_j', count=2, wait=10) is None
    # let a worker handle them
    result_queue = Queue()
    worker(task_queue, result_queue, Value('f', -1))
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
    # check fetch, result by name
    assert fetch(result_j.name) == result_j
    assert result(result_j.name) == result_j.result
    # groups
    assert result_group('test_j')[0] == result_j.result
    assert result_j.group_result()[0] == result_j.result
    assert result_group('test_j', failures=True)[0] == result_j.result
    assert result_j.group_result(failures=True)[0] == result_j.result
    assert fetch_group('test_j')[0].id == [result_j][0].id
    assert fetch_group('test_j', failures=False)[0].id == [result_j][0].id
    assert count_group('test_j') == 1
    assert result_j.group_count() == 1
    assert count_group('test_j', failures=True) == 0
    assert result_j.group_count(failures=True) == 0
    assert delete_group('test_j') == 1
    assert result_j.group_delete() == 0
    deleted_group = delete_group('test_j', tasks=True)
    assert deleted_group is None or deleted_group[0] == 0  # Django 1.9
    deleted_group = result_j.group_delete(tasks=True)
    assert deleted_group is None or deleted_group[0] == 0  # Django 1.9
    # task k should not have been saved
    assert fetch(k) is None
    assert fetch(k, 100) is None
    assert result(k, 100) is None
    broker.delete_queue()


@pytest.mark.django_db
def test_timeout(broker):
    # set up the Sentinel
    broker.list_key = 'timeout_test:q'
    broker.purge_queue()
    async('django_q.tests.tasks.count_forever', broker=broker)
    start_event = Event()
    stop_event = Event()
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, broker=broker, timeout=1)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    broker.delete_queue()


@pytest.mark.django_db
def test_timeout_override(broker):
    # set up the Sentinel
    broker.list_key = 'timeout_override_test:q'
    async('django_q.tests.tasks.count_forever', broker=broker, timeout=1)
    start_event = Event()
    stop_event = Event()
    # Set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, broker=broker, timeout=10)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    broker.delete_queue()


@pytest.mark.django_db
def test_recycle(broker, monkeypatch):
    # set up the Sentinel
    broker.list_key = 'test_recycle_test:q'
    async('django_q.tests.tasks.multiply', 2, 2, broker=broker)
    async('django_q.tests.tasks.multiply', 2, 2, broker=broker)
    async('django_q.tests.tasks.multiply', 2, 2, broker=broker)
    start_event = Event()
    stop_event = Event()
    # override settings
    monkeypatch.setattr(Conf, 'RECYCLE', 2)
    monkeypatch.setattr(Conf, 'WORKERS', 1)
    # set a timer to stop the Sentinel
    threading.Timer(3, stop_event.set).start()
    s = Sentinel(stop_event, start_event, broker=broker)
    assert start_event.is_set()
    assert s.status() == Conf.STOPPED
    assert s.reincarnations == 1
    async('django_q.tests.tasks.multiply', 2, 2, broker=broker)
    async('django_q.tests.tasks.multiply', 2, 2, broker=broker)
    task_queue = Queue()
    result_queue = Queue()
    # push two tasks
    pusher(task_queue, stop_event, broker=broker)
    pusher(task_queue, stop_event, broker=broker)
    # worker should exit on recycle
    worker(task_queue, result_queue, Value('f', -1))
    # check if the work has been done
    assert result_queue.qsize() == 2
    # save_limit test
    monkeypatch.setattr(Conf, 'SAVE_LIMIT', 1)
    result_queue.put('STOP')
    # run monitor
    monitor(result_queue)
    assert Success.objects.count() == Conf.SAVE_LIMIT
    broker.delete_queue()


@pytest.mark.django_db
def test_bad_secret(broker, monkeypatch):
    broker.list_key = 'test_bad_secret:q'
    async('math.copysign', 1, -1, broker=broker)
    stop_event = Event()
    stop_event.set()
    start_event = Event()
    s = Sentinel(stop_event, start_event, broker=broker, start=False)
    Stat(s).save()
    # change the SECRET
    monkeypatch.setattr(Conf, "SECRET_KEY", "OOPS")
    stat = Stat.get_all()
    assert len(stat) == 0
    assert Stat.get(s.parent_pid) is None
    task_queue = Queue()
    pusher(task_queue, stop_event, broker=broker)
    result_queue = Queue()
    task_queue.put('STOP')
    worker(task_queue, result_queue, Value('f', -1), )
    assert result_queue.qsize() == 0
    broker.delete_queue()


@pytest.mark.django_db
def test_bad_broker(broker, mocker):
    mocker.patch.object(broker, 'set_stat',
        side_effect=Exception('Unusable connection'))
    stop_event = Event()
    stop_event.set()
    start_event = Event()
    s = Sentinel(stop_event, start_event, broker=broker, start=False)
    mock_close = mocker.patch.object(broker, 'close')
    Stat(s).save()
    assert mock_close.called


@pytest.mark.django_db
def test_update_failed(broker):
    tag = uuid()
    task = {'id': tag[1],
            'name': tag[0],
            'func': 'math.copysign',
            'args': (1, -1),
            'kwargs': {},
            'started': timezone.now(),
            'stopped': timezone.now(),
            'success': False,
            'result': None}
    # initial save - no success
    save_task(task, broker)
    assert Task.objects.filter(id=task['id']).exists()
    saved_task = Task.objects.get(id=task['id'])
    assert saved_task.success is False
    sleep(0.5)
    # second save - no success
    old_stopped = task['stopped']
    task['stopped'] = timezone.now()
    save_task(task, broker)
    saved_task = Task.objects.get(id=task['id'])
    assert saved_task.stopped > old_stopped
    # third save - success
    task['stopped'] = timezone.now()
    task['result'] = 'result'
    task['success'] = True
    save_task(task, broker)
    saved_task = Task.objects.get(id=task['id'])
    assert saved_task.success is True
    # fourth save - no success
    task['result'] = None
    task['success'] = False
    task['stopped'] = old_stopped
    save_task(task, broker)
    # should not overwrite success
    saved_task = Task.objects.get(id=task['id'])
    assert saved_task.success is True
    assert saved_task.result == 'result'


@pytest.mark.django_db
def assert_result(task):
    assert task is not None
    assert task.success is True
    assert task.result == 1506


@pytest.mark.django_db
def assert_bad_result(task):
    assert task is not None
    assert task.success is False
