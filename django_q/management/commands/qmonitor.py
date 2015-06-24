from django.core.management.base import BaseCommand
from blessed import Terminal
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

from django_q.core import Stat, RUNNING, STOPPED


class Command(BaseCommand):
    help = "Monitors cluster activity"

    def handle(self, *args, **options):
        term = Terminal()
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
                print(term.move(0, 6 * col_width) + term.black_on_green(term.center('Deaths', width=col_width - 1)))
                print(term.move(0, 7 * col_width) + term.black_on_green(term.center('Uptime', width=col_width - 1)))
                i = 2
                stats = Stat.get_all()
                print(term.clear_eos())
                for stat in stats:
                    # color status
                    if stat.status == RUNNING:
                        status = term.green(RUNNING)
                    elif stat.status == STOPPED:
                        status = term.red(STOPPED)
                    else:
                        status = term.yellow(stat.status)
                    # format uptime
                    uptime = (timezone.now() - timezone.make_aware(stat.tob)).total_seconds()
                    hours, remainder = divmod(uptime, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    uptime = '%d:%02d:%02d' % (hours, minutes, seconds)
                    print(term.move(i, 0) + term.center('{}'.format(stat.host), width=col_width - 1))
                    print(term.move(i, 1 * col_width) + term.center('{}'.format(stat.cluster_id), width=col_width - 1))
                    print(term.move(i, 2 * col_width) + term.center('{}'.format(status), width=col_width - 1))
                    print(term.move(i, 3 * col_width) + term.center('{}'.format(len(stat.workers)), width=col_width - 1))
                    print(term.move(i, 4 * col_width) + term.center('{}'.format(stat.task_q_size), width=col_width - 1))
                    print(term.move(i, 5 * col_width) + term.center('{}'.format(stat.done_q_size), width=col_width - 1))
                    print(term.move(i, 6 * col_width) + term.center('{}'.format(stat.reincarnations), width=col_width - 1))
                    print(term.move(i, 7 * col_width) + term.center('{}'.format(uptime), width=col_width - 1))
                    i += 1
                print(term.move(i + 2, 0) + term.center('[Press q to quit]'))
                val = term.inkey(timeout=1)
