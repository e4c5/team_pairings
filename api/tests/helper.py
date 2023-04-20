from django.contrib.auth.models import User
from api import swiss, koth
from tournament.models import Tournament, Director, TournamentRound
from tournament.tools import add_participants, random_results, add_team_members


class Helper:
    def create_tournaments(self):
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


    def add_players(self, tournament, count):
        return add_participants(tournament, use_faker=True, count=count)


    def add_team_members(self, tournament):
        add_team_members(tournament)

        
    def add_results(self, tournament):
        random_results(tournament)

    
    def speed_pair(self, rnd):
        """Pair using swiss and add results"""
        if rnd.pairing_system == TournamentRound.KOTH:
            sp = koth.Koth(rnd)
            sp.make_it()
            sp.save()
            self.add_results(rnd.tournament)

        else:
            sp = swiss.SwissPairing(rnd)
            sp.make_it()
            sp.save()
            self.add_results(rnd.tournament)
