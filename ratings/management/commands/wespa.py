import http.client
from django.core.management.base import BaseCommand, CommandError
from ratings.models import WespaRating
from django.db import transaction

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:

        parser.add_argument('--file', help="the path to the csv file with players",required=False)


    def handle(self, *args, **options):
        if options['file']:
            with open(options['file']) as fp:
                import_ratings(fp)

        else:
            # connect to https://wespa.org/latest.txt using python http client
            # import the ratings into the database
            conn = http.client.HTTPSConnection('wespa.org')
            conn.request("GET", "/latest.txt")
            res = conn.getresponse()
            if res.status == 200:
                content = res.read().decode("utf-8").splitlines()
                import_ratings(content)
            else:
                self.stdout.write(self.style.ERROR('Error connecting to wespa.org\n'))
            
            
def import_ratings(fp):
    """Process the ratings file and add the ratings to the database"""

    with transaction.atomic():
        if type(fp) == list:
            fp = fp[1:]
        else:
            next(fp) # skip header
        for line in fp:
            line = line.strip()
            if line:
                
                values = {
                        'country': line[5:9].strip(),
                        'games': line[30:35].strip(),
                        'rating': line[35:40].strip(),
                        'last': line[40:].strip(),
                    }

                WespaRating.objects.update_or_create(
                    name=line[9:30].strip(),
                    defaults=values
                )
            