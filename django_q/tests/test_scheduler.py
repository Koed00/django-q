from multiprocessing import Queue, Event, Value

import pytest

from django_q.conf import redis_client
from django_q.cluster import pusher, worker, monitor, scheduler
from django_q.tasks import Schedule, fetch, schedule as create_schedule


@pytest.fixture
def r():
    return redis_client


@pytest.mark.django_db
def test_scheduler(r):
    list_key = 'scheduler_test:q'
    r.delete(list_key)
    schedule = create_schedule('math.copysign',
                               1, -1,
                               hook='django_q.tests.tasks.result',
                               schedule_type=Schedule.HOURLY,
                               repeats=1)
    assert schedule.last_run() is None
    # run scheduler
    scheduler(list_key=list_key)
    # set up the workflow
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push it
    pusher(task_queue, stop_event, list_key=list_key, r=r)
    assert task_queue.qsize() == 1
    assert r.llen(list_key) == 0
    task_queue.put('STOP')
    # let a worker handle them
    result_queue = Queue()
    worker(task_queue, result_queue, Value('b', -1))
    assert result_queue.qsize() == 1
    result_queue.put('STOP')
    # store the results
    monitor(result_queue)
    assert result_queue.qsize() == 0
    schedule = Schedule.objects.get(pk=schedule.pk)
    assert schedule.repeats == 0
    assert schedule.last_run() is not None
    assert schedule.success() is True
    task = fetch(schedule.task)
    assert task is not None
    assert task.success is True
    assert task.result < 0
    for t in Schedule.TYPE:
        schedule = create_schedule('django_q.tests.tasks.word_multiply',
                                   2,
                                   word='django',
                                   schedule_type=t[0],
                                   repeats=1,
                                   hook='django_q.tests.tasks.result'
                                   )
        assert schedule is not None
        assert schedule.last_run() is None
    scheduler()
