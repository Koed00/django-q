from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from django_q.monitor import memory


class Command(BaseCommand):
    # Translators: help text for qmemory management command
    help = _("Monitors Q Cluster memory usage")

    def handle(self, *args, **options):
        memory()
