from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django_q.conf import Conf
from django_q.monitor import info


class Command(BaseCommand):
    # Translators: help text for qinfo management command
    help = _('General information over all clusters.')

    option_list = BaseCommand.option_list + (
        make_option('--config',
                    action='store_true',
                    dest='config',
                    default=False,
                    help='Print current configuration.'),
    )

    def handle(self, *args, **options):
        if options.get('config', False):
            hide = ['conf', 'IDLE', 'STOPPING', 'STARTING', 'WORKING', 'SIGNAL_NAMES', 'STOPPED']
            settings = [a for a in dir(Conf) if not a.startswith('__') and a not in hide]
            for setting in settings:
                self.stdout.write('{}: {}'.format(setting, getattr(Conf, setting)))
        else:
            info()
