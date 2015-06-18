import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from django_q import Cluster


@pytest.fixture(scope='session')
def cluster():
    return Cluster()


def test_worker(cluster):
    assert len(cluster.stable) == cluster.stable_size
