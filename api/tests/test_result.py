from django.test import TestCase
from django.db.models import Q

from tournament.models import BoardResult, Participant, TournamentRound, Tournament, Result
from tournament.tools import add_participants

from api import swiss
from api.tests.helper import Helper

class BasicTests(TestCase, Helper):
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
        self.t3 = Tournament.objects.create(name='Joust', start_date='2023-02-25',
            rated=False, num_rounds=5)

    def test_update_standings_by_team(self):
        self.add_players(self.t1, 3)
        self.speed_pair(self.t1.rounds.all()[0])
        p1 = Participant.objects.all()[0]
        self.assertEqual(p1.played, 1)
        p1.game_wins = 0
        p1.round_wins = 0
        p1.played = 0
        p1.spread = 0
        p1.save()

        self.t1.update_all_standings()
        p1.refresh_from_db()
        self.assertNotEqual(p1.played, 0)
        self.assertNotEqual(p1.spread, 0)

    def test_update_standings_by_player(self):
        """Team tournaments results are entered for each player"""
        self.add_players(self.t2, 3)
        rnd = self.t2.rounds.all()[0]
        self.speed_pair(rnd)

         # get the result that's not a bye
        r = rnd.results.exclude(p1__name='Bye').exclude(p2__name='Bye')[0]
        p1 = r.p1
        p2 = r.p2

        self.assertEqual(p1.played, 1)
        p1.game_wins = 0
        p1.round_wins = 0
        p1.played = 0
        p1.spread = 0
        p1.save()

        self.t2.update_all_standings()
        p1.refresh_from_db()
        self.assertNotEqual(p1.played, 0)
        self.assertNotEqual(p1.spread, 0)


    def test_update_standings_singles(self):    
        """Edit a score for a singles tournament"""
        self.add_players(self.t3, 3)
        rnd = self.t3.rounds.all()[0]
        self.speed_pair(rnd)
        
        # get the result that's not a bye
        r = rnd.results.exclude(p1__name='Bye').exclude(p2__name='Bye')[0]
        p1 = r.p1
        p2 = r.p2
        
        self.assertEqual(p1.played, 1)
        self.assertNotEqual(p1.name, 'Bye')
        self.assertNotEqual(p2.name, 'Bye')

        p1.game_wins = 0
        p1.round_wins = 0
        p1.played = 0
        p1.spread = 0
        p1.save()

        self.t3.update_all_standings()
        p1.refresh_from_db()
        self.assertNotEqual(p1.played, 0)
        self.assertNotEqual(p1.spread, 0)

    def test_edit_board_result(self):
        self.add_players(self.t2, 2)
        rnd = self.t2.rounds.all()[0]

        sp = swiss.SwissPairing(rnd)
        sp.make_it()
        sp.save()

        for b in BoardResult.objects.all():
            b.score1 = 200
            b.score2 = 200
            b.save()
        
        p1 = self.t2.participants.all()[0]
        p2 = self.t2.participants.all()[1]
        self.assertEquals(p1.round_wins, 0.5)
        self.assertEquals(p1.game_wins, 2.5)

        b.score2 = 300
        b.save()


        p2.refresh_from_db()
        self.assertEquals(p2.round_wins, 1)
        self.assertEquals(p2.game_wins, 3)
        self.assertEquals(p2.spread, 100)

        p1.refresh_from_db()
        self.assertEquals(p1.round_wins, 0)
        self.assertEquals(p1.game_wins, 2)
        self.assertEquals(p1.spread, -100)


    def test_edit_bye(self):
        """The TD might need to edit the bye to impose a penalty"""
        self.add_players(self.t3, 3)
        rnd = self.t3.rounds.all()[0]
        self.speed_pair(rnd)
        
        # get the result that's a bye
        r = rnd.results.filter( Q(p1__name='Bye') | Q(p2__name='Bye'))[0]
        p1 = r.p1
        p2 = r.p2

        if p1.name == 'Bye':
            self.assertEqual(p2.spread, 100)
            r.score2 = 200
            r.save()
            p2.refresh_from_db()
            self.assertEqual(p2.spread, 200)
        else:
            self.assertEqual(p1.spread, 100)
            r.score1 = 200
            r.save()
            p1.refresh_from_db()
            self.assertEqual(p1.spread, 200)


    def test_edit_by_team(self):
        """Editing a score, set it to be a tie"""
        self.add_players(self.t2, 3)
        rnd = self.t2.rounds.all()[0]
        self.speed_pair(rnd)

        r = rnd.results.exclude(p1__name='Bye').exclude(p2__name='Bye')[0]
        w1 = r.p1.game_wins
        w2 = r.p2.game_wins

        r.score1 = r.score2
        r.games_won = 2.5
        r.save()

        r.refresh_from_db()
        
        self.assertNotEqual(w1, r.p1.game_wins)
        self.assertNotEqual(w2, r.p2.game_wins)
        self.assertEquals(r.p1.game_wins, r.p2.game_wins)
        self.assertEqual(r.p1.round_wins, 0.5)

        # ensures that there is a 0.5 in there 
        self.assertEquals( (r.p2.game_wins * 2) % 2, 1)
        self.assertEquals( (r.p1.game_wins * 2) % 2, 1)


