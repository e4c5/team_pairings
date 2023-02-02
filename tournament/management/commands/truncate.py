import faker
from django.core.management.base import BaseCommand
from tournament.models import Tournament
from tournament.tools import truncate_rounds

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('--round', type=int, required=True,
                help='The last round to remain standing')

    def handle(self, *args, **options):
        if options.get('tournament'):
            self.t = Tournament.get_by_name(options.get('tournament'),'')
        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id'))
        
        print("You are about to truncate the tournament", self.t)
        print("All data ater round number", options.get('round'), 'will be deleted')
        print("Are you sure?")
        r = input().strip().lower()
        if r == "y" or r == "yes":
            truncate_rounds(self.t, options.get('round'))