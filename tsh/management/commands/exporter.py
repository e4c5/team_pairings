from django.core.management.base import BaseCommand
from tournament.models import Tournament, Participant, Result
from tsh import tsh

class Command(BaseCommand):
    """Export a tournament into TSH format"""
    def add_arguments(self, parser) -> None:
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('tsh_file', help="the path to the generated 'a.t' file")


    def handle(self, *args, **options):
        if options.get('tournament'):
            self.t = Tournament.objects.prefetch_related('participants'
            ).get(slug=Tournament.tournament_slug(options.get('tournament','')))

        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id')
            ).select_related('participants')

        with open(options['tsh_file'], 'w') as out:
            tsh.tsh_export(self.t, out)