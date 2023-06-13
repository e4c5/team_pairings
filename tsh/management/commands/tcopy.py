from io import StringIO

from django.core.management.base import BaseCommand
from tournament.models import Tournament, Participant, Result
from tsh import tsh

class Command(BaseCommand):
    """Copy source tournament to destination"""
    def add_arguments(self, parser) -> None:
        parser.add_argument('--src-name', help="The name of the source tournament")
        parser.add_argument('--src-id', help="The id of the source tournament")
        parser.add_argument('--dest-name', help="The name of the source tournament")
        parser.add_argument('--dest-id', help="The id of the source tournament")


    def handle(self, *args, **options):
        self.src = None
        self.dest = None

        if options.get('src_name'):
            self.src = Tournament.get_by_name(options.get('src_name'),'')
        elif options.get('src_id'):
            self.src = Tournament.objects.get(pk=options.get('src_id'))
        
        if options.get('dest_name'):
            self.dest = Tournament.get_by_name(options.get('dest_name'),'')
        elif options.get('dest_id'):
            self.dest = Tournament.objects.get(pk=options.get('dest_id'))

        if self.src and self.dest:
            out = StringIO()
            tsh.tsh_export(self.src, out)
            out.seek(0)
            
            results = tsh.tsh_import(out)
            tsh.save_to_db(self.dest, results)

        else:
            self.stderr.write(self.style.ERROR('Please specify the source and the destination'))