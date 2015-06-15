from django.core.management.base import BaseCommand
from django_q.q import Worker


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        q = Worker()
