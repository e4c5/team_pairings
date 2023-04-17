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
            ).exclude(offed=True).exclude(name='Absent'
            ).order_by('round_wins', '-game_wins', '-spread')

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
                # this tournament does not already have a configured bye lets
                # create one.
                bye, _ = Participant.objects.get_or_create(
                    name='Bye', tournament=self.tournament,
                    defaults = {'name': 'Bye', 'rating': 0,  'tournament': self.tournament}
                )
                self.bye = {'name': 'Bye', 
                    'rating': 0, 'opponents': [], 'player': bye,
                    'score': 0, 'game_wins':-1, 'spread': -1}
                self.players.append(self.bye)
            else:
                # we have a bye but the number is odd, that means a withdrawal
                self.players.remove(self.bye)
                self.bye = None
        self.absentees()


    def absentees(self):
        """Assign a forfeit loss to people who are switched off"""
        players = Participant.objects.select_related(
            ).filter(tournament=self.tournament).filter(offed=True)

        for player in players:
            player.mark_absent(self.rnd)
                
            
    def assign_bye(self):
        """Assign the bye to the lowest rank player"""
        if not self.bye:
            return

        players = self.order_players(self.players)

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
            finally by the rating
        """
        sorted_players = sorted(players, reverse=True,
                                key=lambda player: (player['score'], player['game_wins'],
                                                    player['spread'],
                                                    player['player'].white or 0,
                                                    player['rating']))
        return sorted_players

    def save(self):
        results = []
        for pair in self.pairs:
            r = Result.objects.create(round=self.rnd,
                                      starting=pair[0]['player'],
                                      p1=pair[0]['player'], p2=pair[1]['player'])
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