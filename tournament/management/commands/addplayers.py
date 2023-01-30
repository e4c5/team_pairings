from django.core.management.base import BaseCommand, CommandError
from tournament.models import Participant, Tournament
from tournament.tools import add_players

class Command(BaseCommand):

    def handle(self, *args, **options):
        t = Tournament.get_by_name("richmond scrabble showdown u20",'')
        add_players("api/tests/data/teams.csv", t)



        
