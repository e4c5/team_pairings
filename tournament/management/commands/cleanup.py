# this file is for a specific purpose and will be deleted soon
from datetime import date

from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from tournament.models import Tournament, Participant
from profiles.models import Profile



channel_layer = get_channel_layer()

class Command(BaseCommand): 
    '''
    Send messages to various channels or groups
    '''
    
    def handle(self, *args, **kwargs):
        tourneys = Tournament.objects.filter(name__icontains='Junior')

        for t in tourneys:
            u15 = date(year=2009, month=1, day=1)
            u20 = date(year=2004, month=1, day=1)
            if '20' in t.name:
                for participant in t.participants.all():
                    profile = participant.user.profile
                    if profile.date_of_birth >= u15:
                        print(profile.full_name, 'gets relocated', profile.date_of_birth)
                        sub = Tournament.objects.get(name=t.name.replace('20', '15'))
                        participant.tournament = sub
                        participant.save()
                