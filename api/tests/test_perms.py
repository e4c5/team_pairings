import csv
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

        print(f'/api/tournament/{self.t1.id}/participant')

        resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
        self.assertEqual(200, resp.status_code)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', {})
        
        self.assertEquals(resp.status_code, 403)
        

    def test_write_allowed(self):
        """The tournament director should have write access"""
        self.assertEqual(self.t1.start_date,'2023-02-25')        
        self.client.login(username='sri', password='12345')
        resp = self.client.put(f'/api/tournament/{self.t1.id}/',
            {"start_date": "2022-01-01", "name": "changed"})
        
        self.assertEqual(200, resp.status_code)
        t = models.Tournament.objects.get(pk=self.t1.pk)
        self.assertEqual(t.start_date,'2022-01-01')

        resp = self.client.put(f'/api/tournament/{self.t1.id}/participant/',
            {"rating": 100, "name": "unknown"})
        print(resp.data)            
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, models.Participant.objects.count())


    def test_write_not_allowed(self):
        """Other tournament director should not have write access"""
        self.assertEqual(self.t1.start_date,'2023-02-25')        
        self.client.login(username='sri', password='12345')
        resp = self.client.put(f'/api/tournament/{self.t2.id}/',
            {"start_date": "2022-01-01", "name": "changed"})
        
        self.assertEqual(403, resp.status_code)
        t = models.Tournament.objects.get(pk=self.t2.pk)
        self.assertEqual(t.start_date,'2022-01-01')
