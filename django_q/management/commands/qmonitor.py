from django.core.management.base import BaseCommand

from blessed import Terminal
from django.contrib.humanize.templatetags.humanize import naturaltime

from django_q.core import Stat


class Command(BaseCommand):
    help = "Monitors cluster activity"

    def handle(self, *args, **options):
        term = Terminal()
        with term.fullscreen(), term.hidden_cursor(), term.cbreak():
            val = None
            while val not in (u'q', u'Q',):
                print(term.move(0, 0) + term.bold('ID'))
                print(term.move(0, 10) + term.bold('Status'))
                print(term.move(0, 20) + term.bold('Pool'   ))
                print(term.move(0, 30) + term.bold('TQ'))
                print(term.move(0, 40) + term.bold('RQ'))
                print(term.move(0, 50) + term.bold('Deaths'))
                print(term.move(0, 60) + term.bold('Up'))
                i = 2
                stats = Stat.get_all()
                print(term.clear_eos())
                for stat in stats:
                    print(term.move(i, 0) + '{}'.format(stat.cluster_id))
                    print(term.move(i, 10) + '{}'.format(stat.status))
                    print(term.move(i, 20) + '{}'.format(len(stat.workers)))
                    print(term.move(i, 30) + '{}'.format(stat.task_q_size))
                    print(term.move(i, 40) + '{}'.format(stat.done_q_size))
                    print(term.move(i, 50) + '{}'.format(stat.reincarnations))
                    print(term.move(i, 60) + '{}'.format(naturaltime(stat.tob)))
                    i += 1
                print(term.move(i+2, 0) + '[Press q to quit]')
                val = term.inkey(timeout=1)
