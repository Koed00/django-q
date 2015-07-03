# Django
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _


from django_q.monitor import monitor

class Command(BaseCommand):
    # Translators: help text for qmonitor management command
    help = _("Monitors Q Cluster activity")

    def handle(self, *args, **options):
        monitor()


