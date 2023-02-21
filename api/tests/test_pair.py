from unittest.mock import patch
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status
from rest_framework.test import APITestCase

from tournament.models import BoardResult, Participant, TournamentRound, Director, Result
from tournament.tools import add_participants

from api import swiss
from api.tests.helper import Helper

class BasicTests(APITestCase, Helper):
    """Testing the various read and write permissions"""
    
    def setUp(self) -> None:
        """Creates the fixtures.
        
        A couple of tournaments (one named Indian Open and the other Sri 
        Lankan Open) are created and two tournament directors are assigned

        They both have read access to the other's tournament as does any anon
        user. However neither should be able to edit/delete/create stuff in 
        the other director's event.
        """
        self.create_tournaments();

    def test_unauth(self):
        """Test that the pairing endpoint is not accessible unless you are logged"""
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)

        self.client.login(username='ashok', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)
        
        resp = self.client.delete(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)
        
        
    def test_pair_empty(self):
        """Cannot pair a tournament unless you have participants in it!"""
        self.client.login(username='sri', password='12345')
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.get(f'/api/tournament/{self.t1.id}/pair/')
        # get not allowed
        self.assertEqual(405, resp.status_code)

        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/',
            {'id': rnd.id})
        self.assertEqual(200, resp.status_code)

        # does not work because this tournament does not have any participants
        res = Result.objects.all()
        self.assertEqual(res.count(), 0)
        

    def test_simple_swiss(self):
        """Round 1 pairing for a tiny swiss tournament"""
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


    def test_switch_off_odd(self):
        """What happens to the bye when a player is switched off?
        If the tournament previously had an odd number (excluding the bye) 
        then the bye is take off. Similiar if the number of humans was even
        the by has to be added.
        """
        self.add_players(self.t1, 11)
        rnd = self.t1.rounds.get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # the number increases by one because the bye gets added
        self.assertEquals(12, Participant.objects.filter(tournament=self.t1).count())
        
        # the bye should have been assignmed to the player with the lowest rating
        lowest = Participant.objects.filter(
            tournament=self.t1
        ).order_by('rating')[0]
        self.assertEqual('Bye', 
            Result.objects.filter(round=rnd).get(p2=lowest).p2.name
        )

        # need results
        self.assertRaises(ValueError, swiss.SwissPairing, self.t1.rounds.get(round_no=2))
        
        self.add_results(self.t1)

        # should generate valid pairing for round two 
        sp = swiss.SwissPairing(self.t1.rounds.get(round_no=2))
        sp.make_it()
        sp.save()

        # No need of a by at this stage
        self.assertEquals(12, Participant.objects.filter(tournament=self.t1).count())

        # now we fill up with results.
        
        self.add_results(self.t1)

        # now switch off one of the players
        p = Participant.objects.filter(tournament=self.t1)[3]
        p.offed = True
        p.save()

        rnd = self.t1.rounds.get(round_no=3)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # none of the players should have a bye for this round
        for result in Result.objects.filter(round=rnd):
            self.assertTrue(result.p1.name != 'Bye' and result.p2.name != 'Bye')


    def test_switch_off_even(self):
        """What happens to the bye when a player is switched off?
        If the tournament previously an even number of players not counting
        the bye, when we switch off one of the players the total number of
        active players shoudld remain at 12 due to the bye being created/.
        """
        self.add_players(self.t1, 12)
        rnd = self.t1.rounds.get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # now we fill up with results.
        self.add_results(self.t1)

        # now switch off one of the players
        p = Participant.objects.filter(tournament=self.t1)[3]
        p.offed = True
        p.save()
        self.assertEqual(11, Participant.objects.filter(offed=False).count())
        self.assertEqual(1, Participant.objects.filter(offed=True).count())

        rnd = self.t1.rounds.get(round_no=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # now the number increases by one
        self.assertEqual(12, Participant.objects.filter(offed=False).count())

        # the bye should have been assignmed to the player with the lowest pos
        parties = Participant.objects.filter(
            tournament=self.t1
        ).exclude(name='Bye').order_by(
            'round_wins','game_wins', 'spread'
        )
        lowest = parties[0]

        result = Result.objects.get(
            (Q(p1=lowest) | Q(p2=lowest)) & Q(round=rnd)
        )
        
        self.assertTrue('Bye' == result.p1.name or 'Bye' == result.p2.name)

    def test_two_player(self):
        add_participants(self.t1, True, 4)

        rnd1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=2)
        rnd3 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=3)

        # round 2 cannot be paired now without round 1 being pairedd
        self.assertRaises(ValueError, swiss.SwissPairing, rnd2)

        sp = swiss.SwissPairing(rnd1)
        sp.make_it()
        sp.save()

        results = Result.objects.all()
        self.assertEqual(2, results.count())

        # round 2 cannot still be paired results are not yet in
        self.assertRaises(ValueError, swiss.SwissPairing, rnd2)

        results = Result.objects.all()
        r1, r2 = results[0], results[1]

        r1.score1 = 1000
        r1.score2 = 500
        r1.games_won = 4
        r1.save()
        
        r2.score1 = 900
        r2.score2 = 500
        r2.games_won = 3
        r2.save()

        r1.refresh_from_db()
        r2.refresh_from_db()

        self.assertEquals(1, Result.objects.filter(score1=1000).count())
        self.assertEquals(1, r1.p2.game_wins)
        self.assertEquals(4, r1.p1.game_wins)

        # round2 can now be paired.
        sp = swiss.SwissPairing(rnd2)
        sp.make_it()
        sp.save()

        self.assertEqual(4, results.count())

        # round3 cannot be paired
        self.assertRaises(ValueError, swiss.SwissPairing, rnd3)

    def speed_pair(self, rnd):
        """Pair using swiss and add results"""
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()
        self.add_results(rnd.tournament)


    @patch('api.views.broadcast')
    def test_truncate_by_td(self, p):
        """Test that a tournament round can be truncated by a TD
        (provided that the conditions have been met)
        """
        add_participants(self.t1, True, 4)
        self.client.login(username='sri', password='12345')

        rnd1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=2)

        #truncating unpaired round 1 will fail as it's not yet paired
        resp = self.client.post(f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd1.id})
        self.assertEqual(resp.data['status'],'error')
        self.assertEqual(resp.data['message'], 'round not paired')

        # pair round 1, 2
        self.speed_pair(rnd1)
        self.speed_pair(rnd2)

        #truncating unpaired round 1 will fail because 2 is paired
        resp = self.client.post(f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd1.id})
        self.assertEqual(resp.data['status'],'error')
        self.assertEqual(resp.data['message'],'next round already paired')

        # truncating round 2 will fail because validation code was not sent
        resp = self.client.post(f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd2.id})
        self.assertEqual(resp.data['status'],'error')
        self.assertEqual(resp.data['message'],'confirmation code needed')

        # stil doesn't work, the next round is paird
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd1.id})
        self.assertEqual(resp.data['status'],'error')
        self.assertEqual(resp.data['message'],'next round already paired')

        # and before we do the actual truncate, let's see what happens if we
        # call unpair on this
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/unpair/', {'id': rnd2.id})
        self.assertEqual(resp.data['status'],'error')
        self.assertEqual(resp.data['message'],'This round already has results. Delete them first')

        #finally this should work
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd2.id})
        self.assertEqual(resp.data['status'],'ok')


    @patch('api.views.broadcast')
    def test_truncate_others(self, p):
        """Test that a tournament round CANNOT  be truncated"""
        add_participants(self.t1, True, 4)
        rnd1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=2)

        resp = self.client.post(f'/api/tournament/{self.t2.id}/truncate/')
        self.assertEqual(403, resp.status_code)

        self.client.login(username='ashok', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd1.id})
        self.assertEqual(403, resp.status_code)


    @patch('api.views.broadcast')
    def test_enter_results_by_board(self, m):
        """Entering results by board should update standings"""
        self.add_players(self.t2, 10)
        self.add_team_members(self.t2)
        
        rnd1 = TournamentRound.objects.filter(tournament=self.t2).get(round_no=1)
        sp = swiss.SwissPairing(rnd1)
        sp.make_it()
        sp.save()

        r = rnd1.boardresult_set.all()[0]
        self.client.login(username='ashok', password='12345')
        resp = self.client.put(
            f'/api/tournament/{self.t2.id}/result/',
            {
                'board': 1,
                'score1': 100, 'score2': 200,
                'result': r.id
            }
        )

        self.assertEquals(200, resp.status_code, resp.data)
        r.refresh_from_db()
        # gets flipped because of id
        self.assertEqual(r.score2, 200)
        self.assertEqual(r.score1, 100)

        self.assertEquals(BoardResult.objects.count(), 25)
        self.assertEquals(BoardResult.objects.exclude(score1=None).count(), 1)


    @patch('api.views.broadcast')
    def test_enter_results_by_team(self, m):
        """Entering results by team should update standings"""
        self.add_players(self.t1, 10)
        rnd1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        sp = swiss.SwissPairing(rnd1)
        sp.make_it()
        sp.save()

        r = rnd1.results.all()[0]
        self.client.login(username='sri', password='12345')
        resp = self.client.put(
            f'/api/tournament/{self.t1.id}/result/',
            {
                'board': 1,
                'score1': 100, 'score2': 200, 'game_wins': 2,
                'result': r.id
            }
        )
        self.assertEqual(200, resp.status_code, resp.data)
        r.refresh_from_db()
        self.assertEqual(r.score1, 100)
        self.assertEqual(r.score2, 200)


    def test_truncate_standings(self):
        """Truncate should effect the participant objects"""

        self.add_players(self.t1, 10)
        self.add_players(self.t2, 10)
        rnd1_1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd1_2 = TournamentRound.objects.filter(tournament=self.t2).get(round_no=1)
        self.speed_pair(rnd1_1)
        self.speed_pair(rnd1_2)

        # boiler plate out of the way. We should have 10 results (5 each 
        # for the two tournaments). The number of teams with 1 win in each
        # tournament should also be 5
        self.assertEqual(Result.objects.count(), 10)
        winners = self.t1.participants.filter(round_wins=1).count()
        self.assertEquals(winners, 5)

        self.assertEqual(BoardResult.objects.count(), 25)
        winners = self.t2.participants.filter(round_wins=1).count()
        self.assertEquals(winners, 5)

        # quickly fill up the round 2 for the first tournament.
        rnd2_1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=2)
        self.speed_pair(rnd2_1)
        
        self.assertEqual(Result.objects.count(), 15)
        winners = self.t1.participants.filter(round_wins=2).count()
        self.assertGreater(BoardResult.objects.count(), 1)

        # now we will truncate the second round that we just created above.
        self.client.login(username='sri', password='12345')
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd2_1.id})
        
        self.assertEqual(resp.data['status'],'ok')
        
        self.assertEqual(Result.objects.count(), 10)

        winners = self.t1.participants.filter(round_wins=1).count()
        self.assertEquals(winners, 5)


    @patch('api.views.broadcast')
    def test_pair_view(self, m):
        """Test the view
        Much of the backend has already been testing but the view still 
        has a few branches that needs to be covered"""
        add_participants(self.t1, True, 4)
        
        rnd1 = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(403, resp.status_code)

        self.client.login(username='sri', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('ok', resp.data['status'])

        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('already paired', resp.data['message'])

        resp = self.client.post(f'/api/tournament/{self.t1.id}/unpair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('ok', resp.data['status'])

