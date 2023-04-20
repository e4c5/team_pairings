# king of the hill pairing
from tournament.models import Result, Participant

from api.pairing import Pairing

class Koth(Pairing):
    '''King of the Hill Pairing (sucks)'''

    def __init__(self, rnd):
        ''' Creates swiss pairing for the given round
        Arguments: 
            rnd: a TournamentRound instance.
        '''

        super().__init__(rnd)


    def make_it(self):
        if len(self.players) == 0:
            raise ValueError('No players')

        self.assign_bye()

        sorted_players = self.order_players(self.players)
        for i in range(0, len(sorted_players), 2):
            player = sorted_players[i]
            opponent = sorted_players[i + 1]
            p1, p2 = self.return_with_color_preferences(player, opponent)
            self.pairs.append([p1, p2])

        return self.pairs
    
   