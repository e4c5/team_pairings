from django.core.management.base import BaseCommand, CommandError
from api import swiss

class Command(BaseCommand):

    def handle(self, *args, **options):
        p = swiss.DbPairing(1)
    
        for i, match in enumerate(p.make_it()):
            print(i, match[0], match[1]['name'])
        
        p.save()
        
