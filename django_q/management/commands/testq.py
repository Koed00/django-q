from django.core.management.base import BaseCommand

from django_q.apps import defer


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        for i in range(20):
            defer('testq.tasks.multiply', 2, i)
