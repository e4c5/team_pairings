import csv
import json

from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User

from channels.testing import HttpCommunicator

from rest_framework import status
from rest_framework.test import APITestCase

from tournament import models

class BasicTests(APITestCase):
    """Not going to test creating a tournament since that's one off and done in admin"""

    def setUp(self) -> None:
        self.t1 = models.Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5, private=False)

        self.t2 = models.Tournament.objects.create(name='Richmond Showdown U15', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P', num_rounds=5, private=False)
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()
        models.Director.objects.create(tournament=self.t1, user=user)

    def test_create(self):
        # creating a new tournament creates as many rounds as needed automatically
        # but the creat happens in setup
        self.assertEqual(models.TournamentRound.objects.count(), 10)
        self.assertEqual(str(self.t1), "Richmond Showdown U20")

    
    def test_create_post(self):
        """Send a POST to the http end point to create a tournament.
        Needs to be an authenticated user"""
        resp = self.client.post('/api/tournament/', {
            'name': 'joust', 'rounds': 10, 'date': '2023-04-23'
        })
        self.assertEquals(resp.status_code, 403)
        
        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/api/tournament/')

        resp = self.client.post('/api/tournament/', {
            'name': 'joust', 'num_rounds': 10, 'start_date': '2023-04-23'
        })
        self.assertEquals(resp.status_code, 201, resp.data)


    def test_retrieve(self):
        resp = self.client.get(f'/api/tournament/{self.t1.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data['participants'])


    def test_get_by_name(self):
        """Get by name converts name to slug and queries db"""
        t = models.Tournament.get_by_name('Richmond shoWdOwn U20',start_date='2023-01-01')
        self.assertEqual(2, models.Tournament.objects.count())
        self.assertIsNotNone(t)
        self.assertEquals(t.get_absolute_url(), '/tournament/richmond-showdown-u20/')

        t = models.Tournament.get_by_name('NOT THERE', start_date='2023-01-01')
        
        self.assertEqual(2, models.Tournament.objects.count())
        self.assertIsNone(t)


    def test_seed(self):
        """Test that participants get the right seed"""
        p = models.Participant.objects.create(name="bada", tournament=self.t1)
        self.assertEqual(p.seed, 1)
        p.name = 'renamed'
        p.save()
        p = models.Participant.objects.all()[0]
        self.assertEqual(p.seed, 1)
        p = models.Participant.objects.create(name="bada", tournament=self.t1)
        self.assertEqual(p.seed, 2)


    def test_list(self):
        '''Test that the team list is created correctly'''
        response = self.client.get('/api/tournament/',format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.data))
        self.assertEqual('richmond-showdown-u20', response.data[0]['slug'])


    @patch('api.views.broadcast')
    def test_add_teams(self, m):
        with open('api/tests/data/teams.csv') as fp:
            resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', 
                    {"name": 'aa', "rating":  100})
            self.assertEqual(403, resp.status_code)
             
            self.client.login(username='testuser', password='12345')
            reader = csv.reader(fp)
            for line in reader:
                resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', 
                    {"name": line[0], "rating":  line[1]})
                self.assertEqual(201, resp.status_code)
            
            resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
            self.assertEqual(200, resp.status_code)
            self.assertEqual(18, len(resp.data))


    def test_unauth(self):
        """Test that our endpoints are read only for anonymous users"""
        resp = self.client.post('/api/tournament/', {})
        self.assertEquals(resp.status_code, 403)

        resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
        self.assertEqual(200, resp.status_code)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', {})
        
        self.assertEquals(resp.status_code, 403)
        
    def test_private(self):
        """Only owners can see their tournaments in the list"""
        resp = self.client.get('/api/tournament/')
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(2, len(resp.data), resp.data)

        models.Tournament.objects.update(private=True)
        resp = self.client.get('/api/tournament/')
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(0, len(resp.data), resp.data)

        self.client.login(username='testuser', password='12345')        
        resp = self.client.get('/api/tournament/')
        models.Tournament.objects.update(private=True)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(1, len(resp.data), resp.data)
