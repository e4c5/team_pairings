# this file is for a specific purpose and will be deleted soon
from datetime import date

from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from tournament.models import Tournament, Participant
from profiles.models import Profile
from ratings.models import NationalRating


channel_layer = get_channel_layer()

class Command(BaseCommand): 
    '''
    Send messages to various channels or groups
    '''
    
    def handle(self, *args, **kwargs):
        tourneys = [Tournament.objects.get(id=66)]
        #Tournament.objects.filter(name__icontains='Junior').filter(name__contains='2024').filter(name__icontains='Central')

        for t in tourneys:
            u15 = date(year=2010, month=1, day=1)
            u20 = date(year=2005, month=1, day=1)
            if '20' in t.name:
                for participant in t.participants.all():
                    if participant.user:
                        profile = participant.user.profile
                        if profile.date_of_birth >= u15:
                            print(profile.full_name, 'gets relocated', profile.date_of_birth)
                            try:
                                sub = Tournament.objects.get(id=71) #name=t.name.replace('Under 20', 'Under 15'))
                                participant.tournament = sub
                                participant.save()
                            except Tournament.DoesNotExist:
                                print('This has no junior')

            for participant in t.participants.all():
                try:
                    nr = NationalRating.objects.get(name=participant.name)
                    participant.rating = nr.rating
                    participant.save()
                    print(participant.name, participant.rating)
                except NationalRating.DoesNotExist:
                    participant.rating = 100
                    participant.save()
                    print(participant.name)
                    pass