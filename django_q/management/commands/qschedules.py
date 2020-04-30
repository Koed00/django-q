from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django_q.apps import load_registered_schedules


class Command(BaseCommand):
    # Translators: help text for qinfo management command
    help = _('Recreate registered schedules.')

    def handle(self, *args, **options):
        load_registered_schedules()
