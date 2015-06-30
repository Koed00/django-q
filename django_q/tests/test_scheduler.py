from multiprocessing import Queue, Event
import pytest
from django_q.core import scheduler, pusher, worker, monitor, redis_client
from django_q import Schedule, get_task

@pytest.fixture
def r():
    return redis_client

@pytest.mark.django_db
def test_scheduler(r):
    list_key = 'scheduler_test:q'
    r.delete(list_key)
    schedule = Schedule.objects.create(func='math.copysign',
                                       args='1, -1',
                                       schedule_type=Schedule.ONCE,
                                       repeats=1,
                                       hook='django_q.tests.tasks.result'
                                       )
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
    worker(task_queue, result_queue)
    assert result_queue.qsize() == 1
    result_queue.put('STOP')
    # store the results
    monitor(result_queue)
    assert result_queue.qsize() == 0
    schedule.refresh_from_db()
    assert schedule.repeats == 0
    assert schedule.success() is True
    task = get_task(schedule.task)
    assert task is not None
    assert task.success is True
    assert task.result < 0
