# Django
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django_q.monitor import monitor, info


class Command(BaseCommand):
    # Translators: help text for qmonitor management command
    help = _("Monitors Q Cluster activity")

    option_list = BaseCommand.option_list + (
        make_option('--run-once',
                    action='store_true',
                    dest='run_once',
                    default=False,
                    help='Run once and then stop.'),
        make_option('-i', '--info',
                    action='store_true',
                    dest='info',
                    default=False,
                    help='Lists general information over all clusters. ')
    )

    def handle(self, *args, **options):
        if options.get('info', False):
            info()
        else:
            monitor(run_once=options.get('run_once', False))

