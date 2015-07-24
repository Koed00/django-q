import socket

# external
from blessed import Terminal

# django
from django.utils import timezone
from django.utils.translation import ugettext as _

# local
import signing
from django_q.conf import Conf, redis_client, logger


def monitor(run_once=False):
    term = Terminal()
    r = redis_client
    try:
        redis_client.ping()
    except Exception as e:
        print(term.red('Can not connect to Redis server.'))
        logger.exception(e)
        raise e
    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        val = None
        start_width = int(term.width / 8)
        while val not in (u'q', u'Q',):
            col_width = int(term.width / 8)
            # In case of resize
            if col_width != start_width:
                print(term.clear)
                start_width = col_width
            print(term.move(0, 0) + term.black_on_green(term.center(_('Host'), width=col_width - 1)))
            print(term.move(0, 1 * col_width) + term.black_on_green(term.center(_('Id'), width=col_width - 1)))
            print(term.move(0, 2 * col_width) + term.black_on_green(term.center(_('State'), width=col_width - 1)))
            print(term.move(0, 3 * col_width) + term.black_on_green(term.center(_('Pool'), width=col_width - 1)))
            print(term.move(0, 4 * col_width) + term.black_on_green(term.center(_('TQ'), width=col_width - 1)))
            print(term.move(0, 5 * col_width) + term.black_on_green(term.center(_('RQ'), width=col_width - 1)))
            print(term.move(0, 6 * col_width) + term.black_on_green(term.center(_('RC'), width=col_width - 1)))
            print(term.move(0, 7 * col_width) + term.black_on_green(term.center(_('Up'), width=col_width - 1)))
            i = 2
            stats = Stat.get_all(r=r)
            print(term.clear_eos())
            for stat in stats:
                status = stat.status
                # color status
                if stat.status == Conf.WORKING:
                    status = term.green(str(Conf.WORKING))
                elif stat.status == Conf.STOPPING:
                    status = term.yellow(str(Conf.STOPPING))
                elif stat.status == Conf.STOPPED:
                    status = term.red(str(Conf.STOPPED))
                elif stat.status == Conf.IDLE:
                    status = str(Conf.IDLE)
                # color q's
                tasks = str(stat.task_q_size)
                if stat.task_q_size > 0:
                    tasks = term.cyan(str(stat.task_q_size))
                    if Conf.QUEUE_LIMIT and stat.task_q_size == Conf.QUEUE_LIMIT:
                        tasks = term.green(str(stat.task_q_size))
                results = stat.done_q_size
                if results > 0:
                    results = term.cyan(str(results))
                # color workers
                workers = len(stat.workers)
                if workers < Conf.WORKERS:
                    workers = term.yellow(str(workers))
                # format uptime
                uptime = (timezone.now() - stat.tob).total_seconds()
                hours, remainder = divmod(uptime, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime = '%d:%02d:%02d' % (hours, minutes, seconds)
                # print to the terminal
                print(term.move(i, 0) + term.center(stat.host[:col_width - 1], width=col_width - 1))
                print(term.move(i, 1 * col_width) + term.center(stat.cluster_id, width=col_width - 1))
                print(term.move(i, 2 * col_width) + term.center(status, width=col_width - 1))
                print(term.move(i, 3 * col_width) + term.center(workers, width=col_width - 1))
                print(term.move(i, 4 * col_width) + term.center(tasks, width=col_width - 1))
                print(term.move(i, 5 * col_width) + term.center(results, width=col_width - 1))
                print(term.move(i, 6 * col_width) + term.center(stat.reincarnations, width=col_width - 1))
                print(term.move(i, 7 * col_width) + term.center(uptime, width=col_width - 1))
                i += 1
            # for testing
            if run_once:
                return Stat.get_all(r=r)
            print(term.move(i + 2, 0) + term.center(_('[Press q to quit]')))
            val = term.inkey(timeout=1)


class Status(object):

    """Cluster status base class."""

    def __init__(self, pid):
        self.workers = []
        self.tob = None
        self.reincarnations = 0
        self.cluster_id = pid
        self.sentinel = 0
        self.status = Conf.STOPPED
        self.done_q_size = 0
        self.host = socket.gethostname()
        self.monitor = 0
        self.task_q_size = 0
        self.pusher = 0
        self.timestamp = timezone.now()


class Stat(Status):

    """Status object for Cluster monitoring."""

    def __init__(self, sentinel):
        super(Stat, self).__init__(sentinel.parent_pid or sentinel.pid)
        self.r = sentinel.r
        self.tob = sentinel.tob
        self.reincarnations = sentinel.reincarnations
        self.sentinel = sentinel.pid
        self.status = sentinel.status()
        self.done_q_size = sentinel.result_queue.qsize()
        if sentinel.monitor:
            self.monitor = sentinel.monitor.pid
        self.task_q_size = sentinel.task_queue.qsize()
        if sentinel.pusher:
            self.pusher = sentinel.pusher.pid
        self.workers = [w.pid for w in sentinel.pool]

    def uptime(self):
        return (timezone.now() - self.tob).total_seconds()

    @property
    def key(self):
        """
        :return: redis key for this cluster statistic
        """
        return self.get_key(self.cluster_id)

    @staticmethod
    def get_key(cluster_id):
        """
        :param cluster_id: cluster ID
        :return: redis key for the cluster statistic
        """
        return '{}:{}'.format(Conf.Q_STAT, cluster_id)

    def save(self):
        try:
            self.r.set(self.key, signing.SignedPackage.dumps(self, True), 3)
        except Exception as e:
            logger.error(e)

    def empty_queues(self):
        return self.done_q_size + self.task_q_size == 0

    @staticmethod
    def get(cluster_id, r=redis_client):
        """
        gets the current status for the cluster
        :param cluster_id: id of the cluster
        :return: Stat or Status
        """
        key = Stat.get_key(cluster_id)
        if r.exists(key):
            pack = r.get(key)
            try:
                return signing.SignedPackage.loads(pack)
            except signing.BadSignature:
                return None
        return Status(cluster_id)

    @staticmethod
    def get_all(r=redis_client):
        """
        Get the status for all currently running clusters with the same prefix
        and secret key.
        :return: list of type Stat
        """
        stats = []
        keys = r.keys(pattern='{}:*'.format(Conf.Q_STAT))
        if keys:
            packs = r.mget(keys)
            for pack in packs:
                try:
                    stats.append(signing.SignedPackage.loads(pack))
                except signing.BadSignature:
                    continue
        return stats

    def __getstate__(self):
        # Don't pickle the redis connection
        state = dict(self.__dict__)
        del state['r']
        return state
