from django.core.management.base import BaseCommand
from django_q import Cluster


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        q = Cluster()
