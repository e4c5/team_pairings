# this code was imported from the react_pairing project
# it has been cut and chopped, some features that may seem to be missing
# might actually be there

import sys
import os

from tournament.models import Participant, Result, TournamentRound
from django.db.models import Q

class Pairing:
    ''' Pairing from tournament results stored in a Database '''

    def __init__(self, rnd):
        ''' Creates swiss pairing for the given round
        Arguments: 
            rnd: a TournamentRound instance.
        Throws: value error if this round cannot be paired
        '''

        if rnd.based_on > 0:
            prev = TournamentRound.objects.filter(tournament=rnd.tournament
                    ).get(round_no=rnd.based_on)
            results = Result.objects.filter(round=prev)
            if results.count() < Participant.objects.filter(tournament=rnd.tournament).count() / 2:
                raise ValueError(f"round {rnd.based_on} needs to be completed")
            if results.filter(score1=None).exists():
                raise ValueError(f"round {rnd.based_on} needs to be completed")

        self.pairs = []
        self.tournament = rnd.tournament
        self.players = []
        self.rnd = rnd
        self.next_round = rnd.round_no

        qs = Result.objects.filter(round__round_no__lt=rnd.round_no
                                             ).select_related('p1', 'p2', 'round')

        players = Participant.objects.select_related().filter(tournament_id=self.tournament
                                                              ).exclude(offed=True).order_by('round_wins', '-game_wins', '-spread')
        for pl in players:
            opponents = []
            spread = 0
            wins = 0

            games = qs.filter(Q(p1=pl) | Q(p2=pl)).order_by('-round')
            opponents = []
            for game in games:
                if game.p1.id == pl.id:
                    opponents.append(game.p2)
                else:
                    opponents.append(game.p1)

            self.players.append(
                {'name': pl.name,
                    'spread': pl.spread,
                    'rating': pl.rating,
                    'player': pl,
                    'game_wins': pl.game_wins,
                    'score': pl.round_wins,
                    'opponents': opponents
                    }
            )

    def save(self):
        for pair in self.pairs:
            Result.objects.create(round=self.rnd,
                                  p1=pair[0]['player'], p2=pair[1]['player'])
