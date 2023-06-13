from django.core.management.base import BaseCommand
from tournament.models import Tournament, Participant, Result
from tsh import tsh

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('tsh_file', help="the path to the 'a.t' file from tsh")


    def handle(self, *args, **options):
        if options.get('tournament'):
            self.t = Tournament.get_by_name(options.get('tournament'),'')
        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id'))

        with open(options['tsh_file']) as fp:
            results = tsh.tsh_import()
            tsh.save_to_db(self.t, results)