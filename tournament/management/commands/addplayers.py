import faker
from django.core.management.base import BaseCommand, CommandError
from tournament.models import Participant, Tournament
from tournament.tools import add_participants, add_team_members

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:
        parser.add_argument('--faker',action='store_true',
            help='Use faker to generate data')
        
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('--add-teams', type=int,
                help='Add this many teams to the tournament')
        parser.add_argument('--add-members', action='store_true')


    def handle(self, *args, **options):

        if options.get('tournament'):
            self.t = Tournament.get_by_name(options.get('tournament'),'')
        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id'))

        if options.get('add_teams'):
            if options.get('faker'):
                add_participants(self.t, use_faker=True, count=options.get('add_teams'))
            else:
                t = Tournament.get_by_name("richmond scrabble showdown u20",'')
                add_participants(self.t, False, filename="api/tests/data/teams.csv")

        if options.get('add_members'):
            add_team_members(self.t)



        
