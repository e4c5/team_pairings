from django.db import transaction
from ratings.models import WespaRating, NationalRating, Unrated

def import_unrated(fp):
    """Process the unrated file and add the unrated players to the database"""

    with transaction.atomic():
        if type(fp) == list:
            fp = fp[1:]
        else:
            next(fp) # skip header
        for line in fp:
            line = line.strip()
            if line:
                Unrated.objects.update_or_create(
                    name=line.strip()
                )

def import_ratings(fp, wespa=False):
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
                
                if wespa:
                    WespaRating.objects.update_or_create(
                        name=line[9:30].strip(),
                        defaults=values
                    )
                else:

                    NationalRating.objects.update_or_create(
                        name=line[9:30].strip(),
                        defaults=values
                    )
            