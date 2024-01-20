import csv
import json

from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from channels.testing import HttpCommunicator

from rest_framework import status
from rest_framework.test import APITestCase

from tournament import models
from api.tests.helper import Helper


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
        self.assertEqual(resp.status_code, 403)
        
        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/api/tournament/')

        resp = self.client.post('/api/tournament/', {
            'name': 'joust', 'num_rounds': 10, 'start_date': '2023-04-23', 
            'entry_mode': 'S'
        })
        self.assertEqual(resp.status_code, 201, resp.data)

        t = models.Tournament.objects.order_by('-pk')[0]
        self.assertEqual(t.name,'joust')
        self.assertTrue(t.private)
        self.assertEqual(t.entry_mode, 'S')

        resp = self.client.post('/api/tournament/', {
            'name': 'Richmond', 'num_rounds': 10, 'start_date': '2023-04-23',
            'entry_mode': 'P'
        })
        self.assertEqual(resp.status_code, 201, resp.data)

        t = models.Tournament.objects.order_by('-pk')[0]
        self.assertEqual(t.name,'Richmond')
        self.assertTrue(t.private)
        # does not work because team size is not set
        self.assertEqual(t.entry_mode, 'S')


        resp = self.client.post('/api/tournament/', {
            'name': 'Richmond Teams', 'num_rounds': 10, 'start_date': '2023-04-23',
            'entry_mode': 'P', 'team_size': 5
        })
        self.assertEqual(resp.status_code, 201, resp.data)

        t = models.Tournament.objects.order_by('-pk')[0]
        self.assertEqual(t.name,'Richmond Teams')
        self.assertTrue(t.private)
        self.assertEqual(t.entry_mode, 'P')


    def test_retrieve(self):
        resp = self.client.get(f'/api/tournament/{self.t1.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data['participants'])


    def test_get_by_name(self):
        """Get by name converts name to slug and queries db"""
        t = models.Tournament.get_by_name('Richmond shoWdOwn U20',start_date='2023-01-01')
        self.assertEqual(2, models.Tournament.objects.count())
        self.assertIsNotNone(t)
        self.assertEqual(t.get_absolute_url(), '/tournament/richmond-showdown-u20/')

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
        self.assertEqual('richmond-showdown-u15', response.data[0]['slug'])


    def test_unauth(self):
        """Test that our endpoints are read only for anonymous users"""
        resp = self.client.post('/api/tournament/', {})
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
        self.assertEqual(200, resp.status_code)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', {})
        
        self.assertEqual(resp.status_code, 403)
        
    def test_private(self):
        """Only owners can see their tournaments in the list"""
        resp = self.client.get('/api/tournament/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(2, len(resp.data), resp.data)

        models.Tournament.objects.update(private=True)
        resp = self.client.get('/api/tournament/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(0, len(resp.data), resp.data)

        self.client.login(username='testuser', password='12345')        
        resp = self.client.get('/api/tournament/')
        models.Tournament.objects.update(private=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(1, len(resp.data), resp.data)


class TestParticipants(APITestCase, Helper):

    def setUp(self) -> None:
        self.create_tournaments()
    
    @patch('api.views.broadcast')
    def test_add_teams(self, m):
        with open('api/tests/data/teams.csv') as fp:
            resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', 
                    {"name": 'aa', "rating":  100})
            self.assertEqual(403, resp.status_code)
             
            self.client.login(username='sri', password='12345')
            reader = csv.reader(fp)
            for line in reader:
                resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', 
                    {"name": line[0], "rating":  line[1]})
                self.assertEqual(201, resp.status_code)
            
            resp = self.client.get(f'/api/tournament/{self.t1.id}/participant/')
            self.assertEqual(200, resp.status_code)
            self.assertEqual(18, len(resp.data))


    def test_rr_add(self):
        """adding a participant to an already paired RR should fail"""
        self.t1.round_robin = True
        self.t1.save()
        self.add_players(self.t1, count=10)
        rnd = self.t1.rounds.get(round_no=1)

        self.client.login(username='sri', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd.id})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(f'/api/tournament/{self.t1.id}/participant/', 
                    {"name": "new player", "rating":  100})
        self.assertEqual(400, resp.status_code)

    def test_off_and_delete(self):
        parties = self.add_players(self.t1, count=10)
        self.client.login(username='sri', password='12345')
        resp = self.client.delete(
            f'/api/tournament/{self.t1.id}/participant/{parties[0].id}/'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(9, self.t1.participants.count())

        p = model_to_dict(parties[1])
        p['offed'] = 1
        del p['user']
        del p['payment']
        del p['approved_by']
        
        resp = self.client.put(
            f'/api/tournament/{self.t1.id}/participant/{parties[1].id}/',p
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(1, self.t1.participants.filter(offed=True).count())


    def test_off_and_delete_rr(self):
        """Delete a participant"""
        self.t1.round_robin = True
        self.t1.save()        

        parties = self.add_players(self.t1, count=10)
        self.client.login(username='sri', password='12345')

        # convert parties[0] which is a django model instance into a dictionary
        p = model_to_dict(parties[0])
        p['offed'] = 1
        del p['user']
        del p['payment']
        del p['approved_by']

        resp = self.client.put(
            f'/api/tournament/{self.t1.id}/participant/{parties[0].id}/',p
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.delete(
            f'/api/tournament/{self.t1.id}/participant/{parties[1].id}/'
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(1, self.t1.participants.filter(offed=True).count())

        # we have switched off one player, we have deleted another that means
        # only 8 players are eligible to be paired.
        self.t1.update_num_rounds()
        self.t1.refresh_from_db()

        self.assertEqual(7, self.t1.num_rounds)

        # no we pair this and try to delete someone again. Should not work.
        rnd1 = self.t1.rounds.get(round_no=1)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(resp.status_code, 200)
        rnd1.refresh_from_db()
        self.assertTrue(rnd1.paired)
        
        resp = self.client.delete(
            f'/api/tournament/{self.t1.id}/participant/{parties[2].id}/'
        )
        
        self.assertEqual(resp.status_code, 400)

        # now try to switch someone off.
        p = model_to_dict(parties[5])
        p['offed'] = 1
        del p['user']
        del p['payment']
        del p['approved_by']

        resp = self.client.put(
            f'/api/tournament/{self.t1.id}/participant/{parties[5].id}/',p
        )
        self.assertEqual(resp.status_code, 400)


class RandomFillTests(APITestCase):
    def setUp(self):
        self.td = User.objects.create_user(username='td', password='testpassword')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.tournament = models.Tournament.objects.create(
            name='Test Tournament', private=True, num_rounds=5)
        self.director = models.Director.objects.create(user=self.td, tournament=self.tournament)

    def test_random_fill_private_tournament_as_director(self):
        self.client.force_authenticate(user=self.td)

        url = reverse('tournament-random-fill', kwargs={'pk': self.tournament.pk}) 
        data = {'fill': 5}  # Example data for the 'fill' parameter

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'ok'})

        # Add more assertions to verify the actual changes made by the 'random_fill' function
        # For example, check if the tournament has been filled with random results, etc.

    def test_random_fill_private_tournament_as_regular_user(self):
        # Test random_fill with a regular user who is not a director
        # This should raise a PermissionDenied exception.

        self.client.force_authenticate(user=self.user)

        url = reverse('tournament-random-fill', kwargs={'pk': self.tournament.pk}) 
        data = {'fill': 5}  # Example data for the 'fill' parameter

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_random_fill_public_tournament(self):
        # Test random_fill with a public tournament
        # This should raise a PermissionDenied exception.

        self.tournament.private = False
        self.tournament.save()

        self.client.force_authenticate(user=self.td)

        url = reverse('tournament-random-fill', kwargs={'pk': self.tournament.pk}) 
        data = {'fill': 5}  # Example data for the 'fill' parameter

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
