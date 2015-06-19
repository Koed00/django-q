import sys
import os
from time import sleep

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from django_q import Cluster


@pytest.fixture(scope='session')
def cluster():
    return Cluster()


def test_cluster_initial(cluster):
    cluster.start()
    assert cluster.sentinel.is_alive() is True
    cluster.stop()
    sleep(2)
    assert cluster.sentinel.is_alive() is False
