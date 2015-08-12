import pytest
import redis

from django_q import async
from django_q.cluster import Cluster
from django_q.monitor import monitor, Stat, ping_redis, info


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


@pytest.mark.django_db
def test_ping_redis():
    r = redis.StrictRedis(port=6388)
    with pytest.raises(Exception):
        ping_redis(r)
