from io import StringIO

from faker import Faker

from unittest.mock import patch
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from tournament.models import BoardResult, Participant, TournamentRound, Tournament, Result
from tournament.tools import add_participants, truncate_rounds

from api import swiss, koth
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
        self.create_tournaments()

    def test_unauth(self):
        """Test that the pairing endpoint is not accessible unless you are logged"""
        rnd = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)

        self.client.login(username='ashok', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)

        resp = self.client.delete(f'/api/tournament/{self.t1.id}/pair/')
        self.assertEquals(resp.status_code, 403)

    def test_repeats_random_deterministic_scores(self):
        """Some rounds cannot be paired unless a repeat is allowed"""
        Faker.seed(11111)
        self.pair_with_repeats()

    def test_repeats_random_scores(self):
        """Some rounds cannot be paired unless a repeat is allowed"""

        self.pair_with_repeats()

    def pair_with_repeats(self):
        self.assertIsNone(self.t2.get_last_completed())
        self.add_players(self.t2, 4)
        rnd1 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=1)
        self.speed_pair(rnd1)
        self.assertEquals(rnd1, self.t2.get_last_completed())
        rnd2 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=2)
        self.speed_pair(rnd2)
        self.assertEqual(Result.objects.count(), 4)

        # cannot be paired without repeates
        rnd3 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=3)
        self.speed_pair(rnd3)
        self.assertEqual(Result.objects.count(), 6)

        rnd4 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=4)
        self.speed_pair(rnd4)
        self.assertEqual(Result.objects.count(), 6)

        # allow one repeat and this can be paired
        rnd4.repeats = 1
        rnd4.save()
        self.speed_pair(rnd4)
        self.assertEqual(Result.objects.count(), 8)

        # paring one more round should be possible
        rnd5 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=5)
        rnd5.repeats = 1
        self.speed_pair(rnd5)
        self.assertEqual(Result.objects.count(), 10)

        # lets truncate everything
        truncate_rounds(self.t2, 0)
        self.assertEqual(0, Result.objects.filter(round__tournament=self.t2).count())


    def test_pair_empty(self):
        """Cannot pair a tournament unless you have participants in it!"""
        self.client.login(username='sri', password='12345')
        rnd = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
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
        self.assertIsNone(self.t1.get_last_completed())
        rnd = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        # no participants
        self.assertRaises(ValueError, sp.make_it)

        # odd number with no bye
        sp = swiss.SwissPairing(rnd)
        p1 = Participant.objects.create(
            tournament=self.t1, name='bada', rating=1)
        self.assertRaises(ValueError, sp.make_it)

        # one player with a bye should work
        bye = Participant.objects.create(
            tournament=self.t1, name='Bye', rating=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()
        res = Result.objects.all()
        self.assertEqual(res.count(), 1)
        self.assertEqual(res[0].p1.id, p1.id)
        self.assertEqual(res[0].p2.id, bye.id)
        self.assertEqual(rnd, self.t1.get_last_completed())


class ByesTests(APITestCase, Helper):
    """Test byes and absentees.
    Also see test_result.py"""

    def setUp(self) -> None:
        self.create_tournaments()
        return super().setUp()

    def test_switch_off_odd(self):
        """What happens to the bye when a player is switched off?
        If the tournament previously had an odd number (excluding the bye) 
        then the bye is taken off. 
        """
        self.add_players(self.t1, 11)
        self.assertEquals(11, Participant.objects.filter(
            tournament=self.t1).count())

        # grab the lowest rated player before we do the pairing. AFterwards
        # that will turn out to be the bye

        lowest = Participant.objects.filter(
            tournament=self.t1
        ).order_by('rating')[0]

        rnd = self.t1.rounds.get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # the number increases by one because the bye gets added
        self.assertEquals(12, Participant.objects.filter(
            tournament=self.t1).count())

        # the bye should have been assignmed to the player with the lowest rating
        byeResult = Result.objects.filter(
            round=rnd).get(Q(p2=lowest) | Q(p1=lowest))
        self.assertIn('Bye', [byeResult.p1.name, byeResult.p2.name])
        # because of the bye, he should now have a score of a 300 and a round win
        lowest.refresh_from_db()
        self.assertEquals(300, lowest.spread)
        self.assertEquals(3, lowest.game_wins)
        self.assertEquals(1, lowest.round_wins)

        # need results
        self.assertRaises(ValueError, swiss.SwissPairing,
                          self.t1.rounds.get(round_no=2))

        self.add_results(self.t1)

        # should generate valid pairing for round two
        sp = swiss.SwissPairing(self.t1.rounds.get(round_no=2))
        sp.make_it()
        sp.save()

        # No need of a bye at this stage
        self.assertEquals(12, Participant.objects.filter(
            tournament=self.t1).count())

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
            self.assertTrue(result.p1.name !=
                            'Bye' and result.p2.name != 'Bye')

    def test_singles_odd(self):
        """Testing an individual tournament with an odd number of players"""
        self.t3 = Tournament.objects.create(name='Joust', start_date='2023-02-25',
                                            rated=False, entry_mode='S', num_rounds=5)

        self.add_players(self.t3, 5)
        rnd = self.t3.rounds.get(round_no=1)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # we have paired the first round. There should be 3 Result objects in
        # the database and we should have one of them to be the bye
        self.assertEquals(3, Result.objects.count())
        bye = Result.objects.get(Q(p1__name='Bye') | Q(p2__name='Bye'))
        self.assertIsNotNone(bye.score1)
        self.assertIsNotNone(bye.score2)

        if (bye.p1.name == 'bye'):
            self.assertEquals(bye.score1, 0)
            self.assertEquals(bye.score2, 100)
        else:
            self.assertEquals(bye.score1, 100)
            self.assertEquals(bye.score2, 0)

        self.add_results(self.t3)

        # now switch off one of the players
        p = self.t3.participants.all()[0]
        p.offed = True
        p.save()

        rnd = self.t3.rounds.get(round_no=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # Second round has been paired and that round should not have a bye
        bye = Result.objects.filter(round=rnd
                                    ).filter(Q(p1__name=bye) | Q(p2__name=bye))
        self.assertEqual(0, bye.count())

    def test_singles_even(self):
        """Stat a singles tournament with even number, switch off one later"""
        Faker.seed(5678)
        
        self.t3 = Tournament.objects.create(name='Joust', start_date='2023-02-25',
                                            rated=False, entry_mode='S', num_rounds=5)

        self.add_players(self.t3, 6)
        rnd = self.t3.rounds.get(round_no=1)
        self.speed_pair(rnd)

        # now switch off one of the players
        p = self.t3.participants.all()[0]
        p.offed = True
        p.save()

        # pair the second round
        rnd = self.t3.rounds.get(round_no=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # Now there are 4 pairing objects. 4 players have been paired against
        # themselves (that's 2).The fifth player has been switched off so he
        # is marked as absent (that's 3) and the sixth player gets a bye
           
        self.assertEquals(4, Result.objects.filter(round=rnd).count())
        bye = Result.objects.get(Q(p1__name='Bye') | Q(p2__name='Bye'))
        self.assertIsNotNone(bye.score1)
        self.assertIsNotNone(bye.score2)

        if (bye.p1.name == 'bye'):
            self.assertEquals(bye.score1, 0)
            self.assertEquals(bye.score2, 100)
        else:
            self.assertEquals(bye.score1, 100)
            self.assertEquals(bye.score2, 0)

        ff = Result.objects.filter(round=rnd).get(Q(p1=p) | Q(p2=p))
        if ff.p1 == p:
            self.assertEquals(ff.score1, 0)
            self.assertEquals(ff.score2, 100)
        else:
            self.assertEquals(ff.score1, 100)
            self.assertEquals(ff.score2, 0)

    def test_forfeit(self):
        """Forfeited games should have a -100 spread for the player"""
        self.add_players(self.t1, 6)
        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        self.speed_pair(rnd1)
        # two players get switched off
        ff1 = self.t1.participants.all()[0]
        ff1.offed = True
        ff1.save()
        ff2 = self.t1.participants.all()[1]
        ff2.offed = True
        ff2.save()

        rnd2 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)
        # may need a repeat to make pairing possible
        rnd2.repeats = 1
        self.speed_pair(rnd2)

        # we had six, two are switch off, so two real pairings + 2 of
        # absents
        self.assertEqual(4, rnd2.results.count())

        # All the players, including those that got switched off should be
        # marked as having played two games
        for p in self.t1.participants.all():
            self.assertEqual(p.played, 2)

        # the switched off players should have 100 points lower than earlier
        self.assertEqual(ff1.spread, self.t1.participants.all()[0].spread+100)
        self.assertEqual(ff2.spread, self.t1.participants.all()[1].spread+100)

        # switch them both back on
        ff1.refresh_from_db()
        ff1.offed = False
        ff2.refresh_from_db()
        ff2.offed = False
        ff1.save()
        ff2.save()
        rnd3 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=3)
        self.speed_pair(rnd3)

        # there should be no byes, and there should be no absents
        for result in rnd3.results.all():
            self.assertNotIn(result.p1.name, ['Absent', 'Bye'])
            self.assertNotIn(result.p2.name, ['Absent', 'Bye'])

    def test_switch_off_even(self):
        """What happens to the bye when a player is switched off?

        If the tournament previously had an even number of players not counting
        the bye, when we switch off one of the players the total number of
        active players shoudld remain unchanged due to the bye being created.

        However the player that got switched off get a forfeit loss, so we need
        to add another kind of bye - into the game. This 'losing bye' is named
        as 'Absent'
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

        # grab the player with the lowest position
        lowest = Participant.objects.filter(
            tournament=self.t1
        ).exclude(name='Bye').order_by('round_wins', 'game_wins', 'spread', '-rating')[0]

        rnd = self.t1.rounds.get(round_no=2)
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        # now the number increases by one
        self.assertEqual(13, Participant.objects.filter(offed=False).count())

        # the bye should have been assigned to the player with the lowest pos
        result = Result.objects.get(
            (Q(p1=lowest) | Q(p2=lowest)) & Q(round=rnd)
        )

        self.assertTrue('Bye' == result.p1.name or 'Bye' == result.p2.name)

    def test_late_comer(self):
        add_participants(self.t1, True, 4)
        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)
        rnd3 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=3)

        self.speed_pair(rnd1)
        self.speed_pair(rnd2)
        self.speed_pair(rnd3)

        self.assertEquals(Result.objects.count(), 6)
        add_participants(self.t1, True, 1)
        self.assertEquals(Result.objects.count(), 9)

    def test_two_player(self):
        add_participants(self.t1, True, 4)

        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)
        rnd3 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=3)

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


class TruncationTests(APITestCase, Helper):

    def setUp(self) -> None:
        self.create_tournaments()
        return super().setUp()

    def test_truncate_standings(self):
        """Truncate should effect the participant objects"""

        self.add_players(self.t1, 10)
        self.add_players(self.t2, 10)
        rnd1_1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        rnd1_2 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=1)
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
        rnd2_1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)
        self.speed_pair(rnd2_1)

        self.assertEqual(Result.objects.count(), 15)
        winners = self.t1.participants.filter(round_wins=2).count()
        self.assertGreater(BoardResult.objects.count(), 1)

        # now we will truncate the second round that we just created above.
        self.client.login(username='sri', password='12345')
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd2_1.id})

        self.assertEqual(resp.data['status'], 'ok')

        self.assertEqual(Result.objects.count(), 10)

        winners = self.t1.participants.filter(round_wins=1).count()
        self.assertEquals(winners, 5)

    @patch('api.views.broadcast')
    def test_truncate_by_td(self, p):
        """Test that a tournament round can be truncated by a TD
        (provided that the conditions have been met)
        """
        add_participants(self.t1, True, 4)
        self.client.login(username='sri', password='12345')

        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)

        # truncating unpaired round 1 will fail as it's not yet paired
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd1.id})
        self.assertEqual(resp.data['status'], 'error')
        self.assertEqual(resp.data['message'], 'round not paired')

        # pair round 1, 2
        self.speed_pair(rnd1)
        self.speed_pair(rnd2)

        # truncating unpaired round 1 will fail because 2 is paired
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd1.id})
        self.assertEqual(resp.data['status'], 'error')
        self.assertEqual(resp.data['message'], 'next round already paired')

        # truncating round 2 will fail because validation code was not sent
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/', {'id': rnd2.id})
        self.assertEqual(resp.data['status'], 'error')
        self.assertEqual(resp.data['message'], 'confirmation code needed')

        # stil doesn't work, the next round is paird
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd1.id})
        self.assertEqual(resp.data['status'], 'error')
        self.assertEqual(resp.data['message'], 'next round already paired')

        # and before we do the actual truncate, let's see what happens if we
        # call unpair on this
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/unpair/', {'id': rnd2.id})
        self.assertEqual(resp.data['status'], 'error')
        self.assertEqual(
            resp.data['message'], 'This round already has results. Delete them first')

        # finally this should work
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/truncate/',
            {'td': 'sri', 'id': rnd2.id})
        self.assertEqual(resp.data['status'], 'ok')

    @patch('api.views.broadcast')
    def test_truncate_others(self, p):
        """Test that a tournament round CANNOT  be truncated"""
        add_participants(self.t1, True, 4)
        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        rnd2 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=2)

        resp = self.client.post(f'/api/tournament/{self.t2.id}/truncate/')
        self.assertEqual(403, resp.status_code)

        self.client.login(username='ashok', password='12345')
        resp = self.client.post(f'/api/tournament/{self.t1.id}/truncate/',
                                {'td': 'sri', 'id': rnd1.id})
        self.assertEqual(403, resp.status_code)


class DataEntryTests(APITestCase, Helper):

    def setUp(self) -> None:
        self.create_tournaments()
        return super().setUp()

    @patch('api.views.broadcast')
    def test_enter_results_by_board(self, m):
        """Entering results by board should update standings"""
        self.add_players(self.t2, 10)
        self.add_team_members(self.t2)

        rnd1 = TournamentRound.objects.filter(
            tournament=self.t2).get(round_no=1)
        sp = swiss.SwissPairing(rnd1)
        sp.make_it()
        sp.save()

        r = rnd1.results.all()[0]
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
        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        sp = swiss.SwissPairing(rnd1)
        sp.make_it()
        sp.save()

        r = rnd1.results.all()[0]
        self.client.login(username='sri', password='12345')
        resp = self.client.put(
            f'/api/tournament/{self.t1.id}/result/',
            {
                'board': 1,
                'score1': 100, 'score2': 200, 'games_won': 2,
                'result': r.id
            }
        )
        self.assertEqual(200, resp.status_code, resp.data)
        r.refresh_from_db()
        self.assertEqual(r.score1, 100)
        self.assertEqual(r.score2, 200)

    @patch('api.views.broadcast')
    def test_pair_view(self, m):
        """Test the view
        Much of the backend has already been testing but the view still 
        has a few branches that needs to be covered"""
        add_participants(self.t1, True, 4)

        rnd1 = TournamentRound.objects.filter(
            tournament=self.t1).get(round_no=1)
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(403, resp.status_code)

        self.client.login(username='sri', password='12345')
        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('ok', resp.data['status'])

        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('already paired', resp.data['message'])

        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/unpair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(
            f'/api/tournament/{self.t1.id}/pair/', {'id': rnd1.id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('ok', resp.data['status'])


class KothTests(APITestCase, Helper):
    def setUp(self) -> None:
        self.create_tournaments()

    def test_odd(self):
        """King of the hill with odd number of players"""
        self.t1.rounds.update(pairing_system=TournamentRound.KOTH)
        self.add_players(self.t1, 5)

        # because of lazy loading of query sets, you better convert this into
        # a list if you want to test after the pairing has actually been done
        players = list(Participant.objects.select_related(
        ).filter(tournament=self.t1
                 ).exclude(offed=True).exclude(name='Absent'
                                               ).order_by('-round_wins', '-game_wins', '-spread', '-rating')
        )

        self.speed_pair(self.t1.rounds.all()[0])

        self.assertEquals(Result.objects.count(), 3)

        # the first result is going to be the bye
        results = Result.objects.all()
        bye = results[0]
        for i in range(1, len(results)):
            r = results[i]
            if r.p1 == players[(i - 1) * 2]:
                self.assertEquals(r.p2, players[(i - 1) * 2 + 1])
            if r.p1 == players[(i - 1) * 2]:
                self.assertEquals(r.p2, players[(i - 1) * 2 + 1])

        self.speed_pair(self.t1.rounds.get(round_no=2))
        self.assertEquals(Result.objects.count(), 6)

        p1, p2 = Participant.objects.order_by(
            '-round_wins', '-game_wins', '-spread')[0:2]

        rnd = self.t1.rounds.get(round_no=3)
        self.assertEquals("Round 3", str(rnd))
        sp = koth.Koth(rnd)
        sp.make_it()
        sp.save()

        r = Result.objects.filter(Q(p1=p1) | Q(p2=p1)).get(round=rnd)
        self.assertTrue((r.p1 == p1 and r.p2 == p2)
                        or (r.p2 == p1 and r.p1 == p2))


class TSHTest(APITestCase, Helper):
    """Tests pairing a tournament that has been imported from tsh"""

    def setUp(self) -> None:
        self.t3 = Tournament.objects.create(name='Joust', start_date='2023-02-25',
                                            rated=False, entry_mode='S', num_rounds=9)

    def test_pair(self):
        out = StringIO()
        call_command(
            'importer', 'api/tests/data/anon1.t', 
            '--tournament_id', self.t3.pk,
            stdout=out
        )

        self.assertEquals(self.t3.participants.count(), 43)
        rnd = self.t3.rounds.get(round_no=7)
        self.assertEquals(rnd.results.count(), 0)

        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        self.assertEquals(rnd.results.count(), 21)