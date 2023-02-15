import csv
import asyncio

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from tournament import models

class BasicTests(APITestCase):
    """Testing the various read and write permissions"""
    
    def setUp(self) -> None:
        """Creates the fixtures.
        
        A couple of tournaments (one named Indian Open and the other Sri 
        Lankan Open) are created and two tournament directors are assigned

        They both have read access to the other's tournament as does any anon
        user. However neither should be able to edit/delete/create stuff in 
        the other director's event.
        """
        self.t1 = models.Tournament.objects.create(name='Sri Lankan open', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)

        self.t2 = models.Tournament.objects.create(name='Indian Open', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P', num_rounds=5)

        user = User.objects.create(username='sri')
        user.set_password('12345')
        user.save()
        models.Director.objects.create(tournament=self.t1, user=user)

        user = User.objects.create(username='ashok')
        user.set_password('12345')
        user.save()
        models.Director.objects.create(tournament=self.t2, user=user)

   
    def test_unauth(self):
        """Test that our endpoints are read only for anonymous users"""
        resp = self.client.post('/api/tournament/', {})
        self.assertEquals(resp.status_code, 403)

        resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
        self.assertEqual(200, resp.status_code)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', {})
        
        self.assertEquals(resp.status_code, 403)
        

    def test_write_allowed(self):
        """The tournament director should have write access"""

        self.assertEqual(self.t1.start_date,'2023-02-25')        
        sri = User.objects.get(username='sri')
        self.assertEquals(1, models.Tournament.objects.filter(director__user=sri).count())

        # edit this tournaments name and start date
        self.client.login(username='sri', password='12345')
        resp = self.client.put(f'/api/tournament/{self.t1.id}/',
            {"start_date": "2022-01-01", "name": "changed"})
        
        self.assertEqual(200, resp.status_code)
        t = models.Tournament.objects.get(pk=self.t1.pk)
        self.assertEqual(t.start_date,'2022-01-01')

        # add a participant
        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/',
            {"rating": 100, "name": "unknown"})
       
        self.assertEqual(201, resp.status_code)
        self.assertEqual(1, models.Participant.objects.count())

        # deleting that participant should also be allowed
        p = models.Participant.objects.all()[0]
        resp = self.client.delete(f'/api/tournament/{self.t1.id}/participant/{p.id}/')

        self.assertEqual(204, resp.status_code)
        self.assertEqual(0, models.Participant.objects.count())


    def test_write_not_allowed(self):
        """Other tournament director should not have write access"""
        self.assertEqual(self.t1.start_date,'2023-02-25')        
        self.client.login(username='sri', password='12345')

        # changing the name of someone elses tournament is not allowed
        resp = self.client.put(f'/api/tournament/{self.t2.id}/',
            {"start_date": "2022-01-01", "name": "changed"})
        
        self.assertEqual(403, resp.status_code)
        t = models.Tournament.objects.get(pk=self.t2.pk)
        self.assertEqual(t.start_date,'2023-02-25')

        # can't add a or delete participant to another TD's event
        resp = self.client.post(f'/api/tournament/{self.t2.id}/participant/',
            {"rating": 100, "name": "unknown"})
        self.assertEqual(403, resp.status_code)

        p = models.Participant.objects.create(tournament=self.t2, name='bada', rating=1)
        resp = self.client.post(f'/api/tournament/{self.t2.id}/participant/{p.id}/')
        self.assertEqual(403, resp.status_code)

        
    def test_pairing(self):
        self.client.login(username='sri', password='12345')
        rnd = models.TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.get(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        # get not allowed
        self.assertEqual(405, resp.status_code)

        resp = self.client.post(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        self.assertEqual(200, resp.status_code)

        # does not work because this tournament does not have any participants
        res = models.Result.objects.all()
        self.assertEqual(res.count(), 0)
        