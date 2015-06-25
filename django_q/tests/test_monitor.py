from django_q.core import Cluster
from django_q.management.commands.qmonitor import monitor


def test_monitor():
    c = Cluster()
    c.start()
    stats = monitor(run_once=True)
    c.stop()
    assert len(stats) > 0
    found_c = False
    for stat in stats:
        if stat.cluster_id == c.pid:
            found_c = True
            break
    assert found_c is True
