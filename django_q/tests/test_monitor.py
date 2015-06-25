from django_q.core import Cluster
from django_q.management.commands.qmonitor import monitor


def test_monitor():
    c = Cluster()
    c.start()
    stats = monitor(run_once=True)
    c.stop()
    assert len(stats) > 0
    assert stats[0].cluster_id == c.pid
