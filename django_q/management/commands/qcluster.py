from django.core.management.base import BaseCommand
from django_q.core import Cluster


class Command(BaseCommand):
    help = "Starts a Django Q Cluster."

    def handle(self, *args, **options):
        q = Cluster()
        q.start()

