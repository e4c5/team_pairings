# this code was imported from the react_pairing project
# it has been cut and chopped, some features that may seem to be missing
# might actually be there.
# The earlier attempt mentioned above borrows this code form
# https://github.com/gnomeby/swiss-system-chess-tournament

import sys
import os

from tournament.models import Participant, Result, TournamentRound
from django.db.models import Q

from tournament.models import Tournament, BoardResult

class Pairing:
    ''' Pairing from tournament results stored in a Database.

    Important notes regarding the treatment of the bye:
    When the TD enters his list of participants he will not type an entry for 
    the bye. Instead when the tournament is being paired this class will 
    count the number of active players and enable disable the bye 
    accordingly.

    The participant labelld as the bye does not have a rank or position. 
    '''

    def __init__(self, rnd):
        ''' Creates pairing for the given round
        Subclasses will implement Swiss and RR etc.
        Arguments: 
            rnd: a TournamentRound instance.
        Throws: value error if this round cannot be paired 

        Before pairing we need to make sure that the previous round has 
        been completed. When lagged draw is used that may not be the round
        immidiately before the current round.

        If the previous round is zero, that means we pair based on ratings

        When the previous round is non zero all active players need to have
        a score before this round can be paired.
        '''
        self.pairs = []
        self.tournament = rnd.tournament
        self.players = []
        self.rnd = rnd
        self.next_round = rnd.round_no
        self.bye = None

        players = Participant.objects.select_related(
            ).filter(tournament=self.tournament
            ).exclude(offed=True).order_by('round_wins', '-game_wins', '-spread')

        if rnd.based_on > 0:
            # this round has a predecessor that needs to be completed.
            prev = TournamentRound.objects.filter(tournament=rnd.tournament
                                                  ).get(round_no=rnd.based_on)
            results = Result.objects.filter(round=prev)
            if results.count() < players.count() // 2:
                raise ValueError(f"round {rnd.based_on} needs to be completed")

            if results.filter(score1=None).exists():
                raise ValueError(f"round {rnd.based_on} needs to be completed")

        # fetch all previous round results so that we know of all the 
        # old pairings
        qs = Result.objects.filter(round__round_no__lt=rnd.round_no
                                   ).select_related('p1', 'p2', 'round')

        for pl in players:
            opponents = []

            games = qs.filter(Q(p1=pl) | Q(p2=pl)).order_by('-round')
            opponents = []
            for game in games:
                if game.p1.id == pl.id:
                    opponents.append(game.p2.name)
                else:
                    opponents.append(game.p1.name)

            record = {'name': pl.name,
                      'spread': pl.spread,
                      'rating': pl.rating,
                      'player': pl,
                      'game_wins': pl.game_wins,
                      'score': pl.round_wins,
                      'opponents': opponents
                      }
            self.players.append(record)

            if pl.name == 'Bye':
                self.bye = record


        if len(self.players) % 2 == 1:
            if not self.bye:
                # this tournament does not already have a configured by lets
                # create one.
                bye = Participant.objects.create(
                    name='Bye', rating=0, tournament=self.tournament
                )
                self.bye = {'name': 'Bye', 
                    'rating': 0, 'opponents': [], 'player': bye,
                    'score': 0, 'game_wins':-1, 'spread': -1}
                self.players.append(self.bye)
            else:
                # we have a bye but the number is odd, that means a withdrawal
                self.players.remove(self.bye)
                self.bye = None

    def assign_bye(self):
        """Assign the bye to the lowest rank player"""
        if not self.bye:
            return

        players = self.order_players(self.players)

        for player in reversed(players):
            if 'Bye' not in player['opponents']:
                if player['name'] != 'Bye':
                    self.pairs.append([player, self.bye])
                    self.players.remove(player)
                    self.players.remove(self.bye)
                    return

    def order_players(self, players):
        sorted_players = sorted(players, reverse=True,
                                key=lambda player: (player['score'], player['game_wins'], player['spread']))
        return sorted_players

    def save(self):
        results = []
        for pair in self.pairs:
            r = Result.objects.create(round=self.rnd,
                                      p1=pair[0]['player'], p2=pair[1]['player'])
            if self.tournament.entry_mode == Tournament.BY_PLAYER:
                for i in range(self.tournament.team_size):
                    BoardResult.objects.create(
                        board=i + 1, team1=r.p1, team2=r.p2, round=self.rnd
                    )
            results.append(r)

        self.rnd.paired = True
        self.rnd.save()
        return results
