import pytest
from django_q import Cluster


@pytest.fixture
def qworker():
    return Cluster()


def test_worker(qworker):
    assert len(qworker.stable) == qworker.stable_size
