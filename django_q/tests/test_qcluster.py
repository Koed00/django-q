import sys
import os
from time import sleep
from multiprocessing import Event

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from django_q import Cluster
from django_q.main import Sentinel


@pytest.fixture(scope='session')
def cluster():
    return Cluster()


def test_cluster_initial(cluster):
    assert cluster.sentinel is None
    cluster.start()
    assert cluster.sentinel.is_alive() is True
    cluster.stop()
    sleep(2)
    assert cluster.sentinel.is_alive() is False

def test_sentinel():
    event = Event()
    sentinel = Sentinel(event)
    sleep(1)
    assert sentinel.monitor_pid > 0
    assert sentinel.pusher_pid > 0
    assert len(sentinel.pool) == sentinel.pool_size + 2
