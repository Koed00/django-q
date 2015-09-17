import pytest

from django_q import async
from django_q.cluster import Cluster
from django_q.monitor import monitor, info
from django_q.status import Stat
from django_q.conf import Conf


@pytest.mark.django_db
def test_monitor():
    assert Stat.get(0).sentinel == 0
    c = Cluster()
    c.start()
    stats = monitor(run_once=True)
    c.stop()
    assert len(stats) > 0
    found_c = False
    for stat in stats:
        if stat.cluster_id == c.pid:
            found_c = True
            assert stat.uptime() > 0
            assert stat.empty_queues() is True
            break
    assert found_c is True
    # test lock size for orm broker
    Conf.ORM = 'default'
    monitor(run_once=True)
    Conf.ORM = None


@pytest.mark.django_db
def test_info():
    info()
    do_sync()
    info()
    for _ in range(24):
        do_sync()
    info()


def do_sync():
    async('django_q.tests.tasks.countdown', 1, sync=True, save=True)
