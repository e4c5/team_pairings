from psycopg2.errors import CheckViolation
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from tournament.models import Tournament, Participant, TournamentRound, Director, Result
from api import swiss
from api.tests.helper import Helper

class BasicTests(APITransactionTestCase, Helper):
    """Tests that db doesnt end up with bad data"""

    def setUp(self) -> None:
        self.create_tournaments()


    def test_rounds(self):
        """Test that the pairing endpoint is not accessible unless you are logged"""
        rnd = TournamentRound.objects.filter(tournament=self.t1).get(round_no=1)
        rnd.based_on = 10
        self.assertRaises(IntegrityError, rnd.save)
        
        rnd.based_on = 0
        rnd.round_no = -1
        self.assertRaises(IntegrityError, rnd.save)
        
        
    def test_participant(self):
        p1 = Participant(name='aa', rating=11, tournament=self.t1)
        p2 = Participant(name='bb', rating=11, tournament=self.t1)
        p1.save()
        p2.save()

        self.assertGreater(p2.id, p1.id)
        r = Result(p1=p2, p2=p1, round=self.t1.rounds.all()[0])
        # this one would get saved because the model swaps the fields
        r.save()

