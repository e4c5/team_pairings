import time
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from tournament import models

class BasicTests(APITestCase):
    """Not going to test creating a tournament since that's one off and done in admin"""
    
    def test_list(self):
        models.Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T')

        models.Tournament.objects.create(name='Richmond Showdown U15', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P')

        
        response = self.client.get('/api/tournament/',format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.data))
        self.assertEqual('richmond-showdown-u20', response.data[0]['slug'])