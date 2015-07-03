from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django_q.cluster import Cluster


class Command(BaseCommand):
    # Translators: help text for qcluster management command
    help = _("Starts a Django Q Cluster.")

    def handle(self, *args, **options):
        q = Cluster()
        q.start()

