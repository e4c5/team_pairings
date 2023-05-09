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

    The participant labelled as the bye does not have a rank or position. 
    Bye has a counterpart calle 'Absent', she gets paired against 'swiched off'
    players. 
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
            ).exclude(name='Absent')

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
        qs = Result.objects.filter(
                Q(round__round_no__lt=rnd.round_no) &
                Q(round__tournament=rnd.tournament)
            ).select_related('p1', 'p2', 'round')

        d = {}
        for pl in players:
            if pl.offed:
                pl.mark_absent(self.rnd)
            else:
                record = {'name': pl.name,
                        'spread': pl.spread,
                        'rating': pl.rating,
                        'player': pl,
                        'pair': False,
                        'game_wins': pl.game_wins,
                        'score': pl.round_wins,
                        'opponents': []
                        }
                if self.tournament.team_size is None:
                    record['score'] = pl.game_wins
                d[pl.id] = record
                if pl.name == 'Bye':
                    self.bye = record

        for r in qs:
            if r.p1.name != 'Absent' and r.p2.name != 'Absent':
                if not r.p2.offed and not r.p1.offed:
                    d[r.p2.pk]['opponents'].append(r.p1.name)
                    d[r.p1.pk]['opponents'].append(r.p2.name)

        self.players = list(d.values())

        if len(self.players) % 2 == 1:
            if not self.bye:
                # this tournament does not already have a configured bye lets
                # create one.
                bye, _ = Participant.objects.get_or_create(
                    name='Bye', tournament=self.tournament,
                    defaults = {'name': 'Bye', 'rating': 0,  'tournament': self.tournament}
                )
                self.bye = {'name': 'Bye', 'pair': False,
                    'rating': 0, 'opponents': [], 'player': bye,
                    'score': 0, 'game_wins':-1, 'spread': -1}
                self.players.append(self.bye)
            else:
                # we have a bye but the number is odd, that means a withdrawal
                self.players.remove(self.bye)
                self.bye = None

            
    def assign_bye(self):
        """Assign the bye to the lowest rank player"""
        players = self.order_players(self.players)
        if not self.bye:
            return

        for player in reversed(players):
            if player['name'] != 'Bye' and player['name'] != 'Absent':
                if 'Bye' not in player['opponents']:
                    self.pairs.append([player, self.bye])
                    self.players.remove(player)
                    self.players.remove(self.bye)
                    return


    def order_players(self, players):
        """Sort the players
        First by round_wins (represented by score in the dictionary)
            then by number of games won (for individual tournaments round_wins wont matter)
            then by the spread, then the number of times they have gone first
            finally by the rating. The list is sorted in place but also returned
        """
        players.sort(reverse=True,
                                key=lambda player: (player['score'], player['game_wins'],
                                                    player['spread'],
                                                    player['player'].white or 0,
                                                    player['rating']))
        return players

    def save(self):
        
        results = []
        for pair in self.pairs:
            r = Result(round=self.rnd,
                      p1=pair[0]['player'], p2=pair[1]['player']
            )
            if r.p1.name != 'Bye' and r.p2.name != 'Bye':
                # nope this and the similiar condition below cannot be merged.
                # they are both needed because saving a result is actually a
                # two step process. Pleae refer to the comments in the result
                # class

                r.starting=pair[0]['player']
            
            r.save()

            if self.tournament.entry_mode == Tournament.BY_PLAYER:
                for i in range(self.tournament.team_size):
                    BoardResult.objects.create(
                        board=i + 1, team1=r.p1, team2=r.p2, round=self.rnd
                    )
            results.append(r)
            if r.p1.name == 'Bye' or r.p2.name == 'Bye':
                self.tournament.score_bye(r)


        self.rnd.paired = True
        self.rnd.save()
        return results

    
    def get_color_preferences(self, player):
        """Find which 'color' the player should be assigned
        white means he goes first and black means second.
        
        A color preference that's negative means this player should go first
        in the next game (if possible) a color preference that's positive 
        means he has to go second
        """
        whites = player['player'].white
        blacks = player['player'].played - whites

        return blacks - whites
    

    def return_with_color_preferences(self, playerA, playerB):
        """Given two players orders them so that the first guy goes first"""
        player1, player2 = self.order_players([playerA, playerB])
        player1_pref = self.get_color_preferences(player1)
        player2_pref = self.get_color_preferences(player2)

        if player1_pref <= -2 or player2_pref >= 2:
            return player1, player2
        elif player1_pref == -1 or player2_pref == 1:
            return player1, player2
        elif player1_pref >= 2 or player2_pref <= -2:
            return player2, player1
        elif player1_pref == 1 or player2_pref == -1:
            return player2, player1

        return player1, player2
