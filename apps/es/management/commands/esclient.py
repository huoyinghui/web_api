from django.core.management.base import BaseCommand
from es.models import ping, create_index, health


class Command(BaseCommand):
    WHICH_CHOICES = [
        health,
        ping, 
        create_index,
    ]
    help = 'which> 0:health, 1:ping, 2:create_index, def:0'

    def add_arguments(self, parser):
        parser.add_argument('which', type=int, default=0)

    def handle(self, **options):
        which = options.get('which', 0) % len(self.WHICH_CHOICES)
        func = self.WHICH_CHOICES[which]
        ret = func()
        self.stdout.write(ret)