import os
from datetime import timedelta
from multiprocessing import Event, Value
from unittest import mock

import arrow
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import override_settings
from django.utils import timezone
from django.utils.timezone import is_naive

from django_q.brokers import Broker, get_broker
from django_q.cluster import monitor, pusher, scheduler, worker, localtime
from django_q.conf import Conf
from django_q.queues import Queue
from django_q.tasks import Schedule, fetch
from django_q.tasks import schedule as create_schedule
from django_q.tests.settings import BASE_DIR
from django_q.tests.testing_utilities.multiple_database_routers import (
    TestingMultipleAppsDatabaseRouter,
    TestingReplicaDatabaseRouter,
)


@pytest.fixture
def broker(monkeypatch) -> Broker:
    """Patches the Conf object setting the DJANGO_REDIS attribute allowing a default redis configuration."""
    monkeypatch.setattr(Conf, "DJANGO_REDIS", "default")
    return get_broker()


@pytest.fixture
def orm_broker(monkeypatch) -> None:
    """Patches the Conf object setting the ORM attribute to a database named default."""
    monkeypatch.setattr(Conf, "ORM", "default")


@pytest.fixture
def orm_no_replica_broker(orm_broker, monkeypatch) -> Broker:
    """Generates a Broker with a disabled read replica database configuration."""
    monkeypatch.setattr(Conf, "HAS_REPLICA", False)
    return get_broker(list_key="scheduler_test:q")


@pytest.fixture
def orm_replica_broker(orm_broker, monkeypatch) -> Broker:
    """Generates a Broker with read replica database configuration."""
    monkeypatch.setattr(Conf, "HAS_REPLICA", True)
    return get_broker(list_key="scheduler_test:q")


REPLICA_DATABASE_ROUTERS = [
    f"{TestingReplicaDatabaseRouter.__module__}.{TestingReplicaDatabaseRouter.__name__}"
]
REPLICA_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
    "replica": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
}

MULTIPLE_APPS_DATABASE_ROUTERS = [
    f"{TestingMultipleAppsDatabaseRouter.__module__}.{TestingMultipleAppsDatabaseRouter.__name__}"
]
MULTIPLE_APPS_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
    "admin": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
}


@pytest.mark.django_db
def test_scheduler(broker, monkeypatch):
    broker.list_key = "scheduler_test:q"
    broker.delete_queue()
    schedule = create_schedule(
        "math.copysign",
        1,
        -1,
        name="test math",
        hook="django_q.tests.tasks.result",
        schedule_type=Schedule.HOURLY,
        repeats=1,
    )
    assert schedule.last_run() is None
    # check duplicate constraint
    with pytest.raises(IntegrityError):
        schedule = create_schedule(
            "math.copysign",
            1,
            -1,
            name="test math",
            hook="django_q.tests.tasks.result",
            schedule_type=Schedule.HOURLY,
            repeats=1,
        )
    # run scheduler
    scheduler(broker=broker)
    # set up the workflow
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push it
    pusher(task_queue, stop_event, broker=broker)
    assert task_queue.qsize() == 1
    assert broker.queue_size() == 0
    task_queue.put("STOP")
    # let a worker handle them
    result_queue = Queue()
    worker(task_queue, result_queue, Value("b", -1))
    assert result_queue.qsize() == 1
    result_queue.put("STOP")
    # store the results
    monitor(result_queue)
    assert result_queue.qsize() == 0
    schedule = Schedule.objects.get(pk=schedule.pk)
    assert schedule.repeats == 0
    assert schedule.last_run() is not None
    assert schedule.success() is True
    assert schedule.next_run < arrow.get(timezone.now()).shift(hours=+1)
    task = fetch(schedule.task)
    assert task is not None
    assert task.success is True
    assert task.result < 0
    # Once schedule with delete
    once_schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="django",
        schedule_type=Schedule.ONCE,
        repeats=-1,
        hook="django_q.tests.tasks.result",
    )
    assert hasattr(once_schedule, "pk") is True
    # negative repeats
    always_schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="django",
        schedule_type=Schedule.DAILY,
        repeats=-1,
        hook="django_q.tests.tasks.result",
    )
    assert hasattr(always_schedule, "pk") is True
    # Minute schedule
    minute_schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="django",
        schedule_type=Schedule.MINUTES,
        minutes=10,
    )
    assert hasattr(minute_schedule, "pk") is True
    # Cron schedule
    cron_schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="django",
        schedule_type=Schedule.CRON,
        cron="0 22 * * 1-5",
    )
    assert hasattr(cron_schedule, "pk") is True
    assert cron_schedule.full_clean() is None
    assert cron_schedule.__str__() == "django_q.tests.tasks.word_multiply"
    with pytest.raises(ValidationError):
        create_schedule(
            "django_q.tests.tasks.word_multiply",
            2,
            word="django",
            schedule_type=Schedule.CRON,
            cron="0 22 * * 1-12",
        )
    # All other types
    for t in Schedule.TYPE:
        if t[0] == Schedule.CRON:
            continue
        schedule = create_schedule(
            "django_q.tests.tasks.word_multiply",
            2,
            word="django",
            schedule_type=t[0],
            repeats=1,
            hook="django_q.tests.tasks.result",
        )
        assert schedule is not None
        assert schedule.last_run() is None
        scheduler(broker=broker)
    # via model
    Schedule.objects.create(
        func="django_q.tests.tasks.word_multiply",
        args="2",
        kwargs='word="django"',
        schedule_type=Schedule.DAILY,
    )
    # scheduler
    scheduler(broker=broker)
    # ONCE schedule should be deleted
    assert Schedule.objects.filter(pk=once_schedule.pk).exists() is False
    # Catch up On
    monkeypatch.setattr(Conf, "CATCH_UP", True)
    now = timezone.now()
    schedule = create_schedule(
        "django_q.tests.tasks.word_multiply",
        2,
        word="catch_up",
        schedule_type=Schedule.HOURLY,
        next_run=timezone.now() - timedelta(hours=12),
        repeats=-1,
    )
    scheduler(broker=broker)
    schedule = Schedule.objects.get(pk=schedule.pk)
    assert schedule.next_run < now
    # Catch up off
    monkeypatch.setattr(Conf, "CATCH_UP", False)
    scheduler(broker=broker)
    schedule = Schedule.objects.get(pk=schedule.pk)
    assert schedule.next_run > now
    # Done
    broker.delete_queue()

    monkeypatch.setattr(Conf, "PREFIX", "some_cluster_name")
    # create a schedule on another cluster
    schedule = create_schedule(
        "math.copysign",
        1,
        -1,
        name="test schedule on a another cluster",
        hook="django_q.tests.tasks.result",
        schedule_type=Schedule.HOURLY,
        cluster="some_other_cluster_name",
        repeats=1,
    )
    # run scheduler
    scheduler(broker=broker)
    # set up the workflow
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push it
    pusher(task_queue, stop_event, broker=broker)

    # queue must be empty
    assert task_queue.qsize() == 0

    monkeypatch.setattr(Conf, "PREFIX", "default")
    # create a schedule on the same cluster
    schedule = create_schedule(
        "math.copysign",
        1,
        -1,
        name="test schedule with no cluster",
        hook="django_q.tests.tasks.result",
        schedule_type=Schedule.HOURLY,
        cluster="default",
        repeats=1,
    )
    # run scheduler
    scheduler(broker=broker)
    # set up the workflow
    task_queue = Queue()
    stop_event = Event()
    stop_event.set()
    # push it
    pusher(task_queue, stop_event, broker=broker)

    # queue must contain a task
    assert task_queue.qsize() == 1


@override_settings(
    DATABASE_ROUTERS=REPLICA_DATABASE_ROUTERS, DATABASES=REPLICA_DATABASES
)
@pytest.mark.django_db
def test_scheduler_atomic_transaction_must_specify_a_database_when_no_replicas_are_used(
    orm_no_replica_broker: Broker,
):
    """
    GIVEN a environment without a read replica database
    WHEN the scheduler is called
    THEN the transaction atomic must be called using the configured database in the Conf.ORM settings.
    """
    broker = orm_no_replica_broker
    with mock.patch("django_q.cluster.db") as mocked_db:
        scheduler(broker=broker)
        # The router should correctly set the database to use!
        mocked_db.transaction.atomic.assert_called_with(using=broker.connection.db)


@override_settings(
    DATABASE_ROUTERS=REPLICA_DATABASE_ROUTERS, DATABASES=REPLICA_DATABASES
)
@pytest.mark.django_db
def test_scheduler_atomic_transaction_must_specify_no_database_when_read_write_replicas_are_used(
    orm_replica_broker: Broker,
):
    """
    GIVEN a environment with a read/write configured replica database
    WHEN the scheduler is called
    THEN the transaction must be called without a specific database, thus letting the database router pick.
    """
    with mock.patch("django_q.cluster.db") as mocked_db:
        scheduler(broker=orm_replica_broker)
        # No specific databases should be set here, this is the job of the router!
        mocked_db.transaction.atomic.assert_called_with()


@override_settings(
    DATABASE_ROUTERS=MULTIPLE_APPS_DATABASE_ROUTERS, DATABASES=MULTIPLE_APPS_DATABASES
)
@pytest.mark.django_db
def test_scheduler_atomic_transaction_must_specify_the_database_based_on_router_redirection(
    orm_no_replica_broker: Broker,
):
    """
    GIVEN a environment without a read replica database
    WHEN the scheduler is called
    THEN the transaction atomic must be called using the configured database in the Conf.ORM settings.
    """
    broker = orm_no_replica_broker
    with mock.patch("django_q.cluster.db") as mocked_db:
        scheduler(broker=broker)
        # The router should correctly set the database to use!
        assert broker.connection.db == "default"
        mocked_db.transaction.atomic.assert_called_with(using=broker.connection.db)


def test_localtime():
    assert not is_naive(localtime())


@override_settings(USE_TZ=False)
def test_naive_localtime():
    assert is_naive(localtime())
