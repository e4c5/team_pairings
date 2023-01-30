from django.core.management.base import BaseCommand, CommandError
from api import swiss
from tournament.models import TournamentRound

class Command(BaseCommand):

    def handle(self, *args, **options):
        rnd = TournamentRound.objects.get(round_no = 1, tournament_id=3)
        p = swiss.DbPairing(rnd)
    
        for i, match in enumerate(p.make_it()):
            print(i, match[0], match[1]['name'])
        
        p.save()
        
