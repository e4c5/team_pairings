import csv
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from tournament.models import Tournament, Participant, TournamentRound, Director, Result
from api import swiss

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
        self.t1 = Tournament.objects.create(name='Sri Lankan open', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='T', num_rounds=5)

        self.t2 = Tournament.objects.create(name='Indian Open', start_date='2023-02-25',
            rated=False, team_size=5, entry_mode='P', num_rounds=5)

        user = User.objects.create(username='sri')
        user.set_password('12345')
        user.save()
        Director.objects.create(tournament=self.t1, user=user)

        user = User.objects.create(username='ashok')
        user.set_password('12345')
        user.save()
        Director.objects.create(tournament=self.t2, user=user)


    def test_unauth(self):
        """Test that the pairing endpoint is not accessible unless you are logged"""
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        self.assertEquals(resp.status_code, 403)

        self.client.login(username='ashok', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        self.assertEquals(resp.status_code, 403)
        
        resp = self.client.delete(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        self.assertEquals(resp.status_code, 403)
        
        
    def test_pair_empty(self):
        self.client.login(username='sri', password='12345')
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.get(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        # get not allowed
        self.assertEqual(405, resp.status_code)

        resp = self.client.post(f'/api/tournament/{self.t1.id}/round/{rnd.id}/pair/')
        self.assertEqual(200, resp.status_code)

        # does not work because this tournament does not have any participants
        res = Result.objects.all()
        self.assertEqual(res.count(), 0)
        

    def test_simplest(self):
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        # no participants
        self.assertRaises(ValueError, sp.make_it)

        # odd number with no bye
        sp = swiss.SwissPairing(rnd)
        p1 = Participant.objects.create(tournament=self.t1, name='bada', rating=1)
        self.assertRaises(ValueError, sp.make_it)

        # one player with a bye should work
        bye = Participant.objects.create(tournament=self.t1, name='Bye', rating=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()
        res = Result.objects.all()
        self.assertEqual(res.count(), 1)
        self.assertEqual(res[0].p1.id, p1.id)
        self.assertEqual(res[0].p2.id, bye.id)
