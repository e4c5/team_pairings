import faker
from django.core.management.base import BaseCommand, CommandError
from tournament.models import Participant, Tournament
from tournament.tools import add_participants, add_team_members

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:

        parser.add_argument('--file', help="the path to the csv file with players",required=False)


    def handle(self, *args, **options):
        pass