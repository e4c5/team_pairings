from django.core.management.base import BaseCommand, CommandError
from tournament.models import Participant
from api import swiss

class Command(BaseCommand):

    def handle(self, *args, **options):
        file = '/tmp/u15.txt'
        with open(file) as fp:
            for i, line in enumerate(fp):
                Participant.objects.create(tournament_id=2, name=line.strip(),
                    seed=(i + 1) * 100)


        
