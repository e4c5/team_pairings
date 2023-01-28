import csv
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from tournament import models

class BasicTests(APITestCase):
    """Not going to test creating a tournament since that's one off and done in admin"""
    
    def setUp(self) -> None:
        self.t1 = models.Tournament.objects.create(name='Richmond Showdown U20', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T')

        self.t2 = models.Tournament.objects.create(name='Richmond Showdown U15', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P')
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()


    def test_create(self):
        t = models.Tournament.get_by_name('Richmond shoWdOwn U20',start_date='2023-01-01')
        self.assertEqual(2, models.Tournament.objects.count())

        t = models.Tournament.get_by_name('THIS WILL BE MADE', start_date='2023-01-01')
        self.assertEquals(t.get_absolute_url(), '/tournament/this-will-be-made/')
        self.assertEqual(3, models.Tournament.objects.count())
        self.assertEqual(t.num_rounds, 0)


    def test_current_round(self):
        for i in range(5):
            models.TournamentRound.objects.create(
                tournament=self.t1, round_no=i+1,
                pairing_system='SWISS',repeats=0,based_on=i,
                num_rounds=5, team_size=5
            )
        self.assertEqual(0, self.t1.current_round)


    def test_list(self):
        '''Test that the team list is created correctly'''
        response = self.client.get('/api/tournament/',format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.data))
        self.assertEqual('richmond-showdown-u20', response.data[0]['slug'])


    def test_add_teams(self):
        with open('api/tests/data/teams.csv') as fp:
            self.client.login(username='testuser', password='12345')
            reader = csv.reader(fp)
            for line in reader:
                resp = self.client.post(f'/api/{self.t1.id}/participant/', 
                    {"name": line[0], "seed":  line[1]})
                self.assertEqual(201, resp.status_code)
            
            resp = self.client.get(f'/api/{self.t1.id}/participant/')
            self.assertEqual(200, resp.status_code)
            self.assertEqual(18, len(resp.data))


    def test_unauth(self):
        """Test that our endpoints are read only for anonymous users"""
        resp = self.client.post('/api/tournament/', {})
        self.assertEquals(resp.status_code, 403)

        resp = self.client.post(f'/api/{self.t1.id}/participant/', {})
        self.assertEquals(resp.status_code, 403)
        