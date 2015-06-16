import pytest
from django_q.apps import Worker


@pytest.fixture
def qworker():
    return Worker()


def test_worker(qworker):
    assert len(qworker.stable) == qworker.stable_size
