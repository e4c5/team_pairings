from django.core.management.base import BaseCommand, CommandError
from ratings.management.importer import import_ratings

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:

        parser.add_argument('--file', help="the path to the csv file with players",\
                            required=True)


    def handle(self, *args, **options):
        with open(options['file']) as fp:
            import_ratings(fp, wespa=False)

            
