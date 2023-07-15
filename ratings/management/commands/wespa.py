import http.client
from django.core.management.base import BaseCommand, CommandError
from ratings.management.importer import import_ratings

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:

        parser.add_argument('--file', help="the path to the csv file with players",required=False)


    def handle(self, *args, **options):
        if options['file']:
            with open(options['file']) as fp:
                import_ratings(fp, wespa=True)

        else:
            # connect to https://wespa.org/latest.txt using python http client
            # import the ratings into the database
            conn = http.client.HTTPSConnection('wespa.org')
            conn.request("GET", "/latest.txt")
            res = conn.getresponse()
            if res.status == 200:
                content = res.read().decode("utf-8").splitlines()
                import_ratings(content, wespa=True)
            else:
                self.stdout.write(self.style.ERROR('Error connecting to wespa.org\n'))

