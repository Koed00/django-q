from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django_q.monitor import info


class Command(BaseCommand):
    # Translators: help text for qinfo management command
    help = _('General information over all clusters.')

    def handle(self, *args, **options):
        info()
