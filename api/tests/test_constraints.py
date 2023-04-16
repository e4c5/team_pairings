from psycopg2.errors import CheckViolation
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from tournament.models import Participant, TournamentRound, BoardResult, Result

from api import swiss
from api.tests.helper import Helper

class BasicTests(APITransactionTestCase, Helper):
    """Tests that db doesnt end up with bad data"""

    def setUp(self) -> None:
        self.create_tournaments()


    def test_rounds(self):
        """A round number has to be valid"""
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd.based_on = 10
        self.assertRaises(IntegrityError, rnd.save)
        
        rnd.based_on = 0
        rnd.round_no = -1
        self.assertRaises(IntegrityError, rnd.save)
        
        
    def test_participant(self):
        """You can't save a result if the two participant ids are not ordered"""
        p1 = Participant(name='aa', rating=11, tournament=self.t1)
        p2 = Participant(name='bb', rating=11, tournament=self.t1)
        p1.save()
        p2.save()

        self.assertGreater(p2.id, p1.id)
        r = Result(p1=p2, p2=p1, round=self.t1.rounds.all()[0])
        # this one would get saved because the model swaps the fields
        r.save()
        r.refresh_from_db()
        # notice the swap
        self.assertEqual(r.p1.id , p1.id)

    def test_participant_order(self):
        """You can't save a result with p1,p2 and then save again as p2,p1"""
        p1 = Participant(name='aa', rating=11, tournament=self.t1)
        p2 = Participant(name='bb', rating=11, tournament=self.t1)
        p1.save()
        p2.save()

        
        r = Result(p1=p2, p2=p1, round=self.t1.rounds.all()[0])
        # this one would get saved because the model swaps the fields
        r.save()

        r = Result(p1=p1, p2=p2, round=self.t1.rounds.all()[0])
        self.assertRaises(IntegrityError, r.save)


    def test_board_result(self):
        """Test that border result team1, team2 are ordered"""
        p1 = Participant(name='aa', rating=11, tournament=self.t1)
        p2 = Participant(name='bb', rating=11, tournament=self.t1)
        p3 = Participant(name='cc', rating=11, tournament=self.t1)
        p4 = Participant(name='dd', rating=11, tournament=self.t1)
        p1.save()
        p2.save()
        p3.save()
        p4.save()

        rnd = self.t1.rounds.all()[0]
        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()
        
        
        b = BoardResult(team1=p1, team2=p1, board=1,
             round=rnd)
        # needs scores
        self.assertRaises(IntegrityError, b.save)
        
        b.score1 = 100
        b.score2 = 100
        b.team1 = p4
        
        # trying to save a mismatched pair. Team 1 did not play team2!
        self.assertRaises(IndexError, b.save)

        r = Result.objects.get(p1=p1)
        b.team1 = r.p1
        b.team2 = r.p2
        b.save()
        b.refresh_from_db()

        self.assertEqual(b.team1.id, r.p1.id)
        self.assertEqual(b.team2.id, r.p2.id)