# Django
from django.core.management.base import BaseCommand
from django.utils import timezone

# External
from blessed import Terminal

# Local
from django_q.core import Stat, redis_client
from django_q.conf import Conf

# TODO add name argument to monitor different clusters

class Command(BaseCommand):
    help = "Monitors cluster activity"

    def handle(self, *args, **options):
        monitor()


def monitor(run_once=False):
    term = Terminal()
    r = redis_client
    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        val = None
        start_width = int(term.width / 8)
        while val not in (u'q', u'Q',):
            col_width = int(term.width / 8)
            # In case of resize
            if col_width != start_width:
                print(term.clear)
                start_width = col_width
            print(term.move(0, 0) + term.black_on_green(term.center('Host', width=col_width - 1)))
            print(term.move(0, 1 * col_width) + term.black_on_green(term.center('Id', width=col_width - 1)))
            print(term.move(0, 2 * col_width) + term.black_on_green(term.center('Status', width=col_width - 1)))
            print(term.move(0, 3 * col_width) + term.black_on_green(term.center('Pool', width=col_width - 1)))
            print(term.move(0, 4 * col_width) + term.black_on_green(term.center('TQ', width=col_width - 1)))
            print(term.move(0, 5 * col_width) + term.black_on_green(term.center('RQ', width=col_width - 1)))
            print(term.move(0, 6 * col_width) + term.black_on_green(term.center('RC', width=col_width - 1)))
            print(term.move(0, 7 * col_width) + term.black_on_green(term.center('Up', width=col_width - 1)))
            i = 2
            stats = Stat.get_all(r=r)
            print(term.clear_eos())
            for stat in stats:
                # color status
                if stat.status == Conf.WORKING:
                    status = term.green(Conf.WORKING)
                elif stat.status == Conf.STOPPED:
                    status = term.red(Conf.STOPPED)
                elif stat.status == Conf.IDLE:
                    status = Conf.IDLE
                else:
                    status = term.yellow(stat.status)
                # color q's
                tasks = stat.task_q_size
                if tasks > 0:
                    tasks = term.cyan(str(tasks))
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
            print(term.move(i + 2, 0) + term.center('[Press q to quit]'))
            val = term.inkey(timeout=1)
