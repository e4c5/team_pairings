# this code was imported from the react_pairing project
# it has been cut and chopped, some features that may seem to be missing
# might actually be there

import sys, os

from tournament.models import Participant, Result, TournamentRound
from django.db.models import Q

class Pairing:
    '''
    Pairing procedure according to Swiss system rules
    
    Originally from: https://github.com/gnomeby/swiss-system-chess-tournament
    Adapted to work with scrabble scores rather than colors.
    '''
    def __init__(self, next_round):
        self.next_round = next_round
        self.pairs = []
                
    def make_it(self):
        if len(self.pairs) % 2 == 1:
            raise ValueError('Odd number of players')
        
        if self.next_round == 1:
            self.pair_first_round()
        elif self.next_round % 2 == 0:
            self.pair_even_round()
        elif self.next_round % 2 == 1:
            self.pair_odd_round()

        return self.pairs

    def get_detailed_pairings(self):
        pairs = []
        for pair in self.s:
            pairs.append(pair)
            pairs.append(pair[1],pair[0])
        
        return sorted(pairs, reverse=True, key=lambda x: (x[0]['score'], x[0]['spread']))

    def order_players(self, players):
        sorted_players = sorted(players, reverse=True, 
                key=lambda player: (player['score'],player['game_wins'], player['spread']))
        return sorted_players
        
    def pair_first_round(self):
        sorted_players = self.order_players(self.players)
        S1count = len(self.players) // 2

        if sorted_players[-1]['name'] == 'bye':
            self.pairs.append([sorted_players[-1],sorted_players[-2]])
            S1count -= 1
            
        for index in range(S1count):
            self.pairs.append([sorted_players[index], sorted_players[S1count+index]])

    
    def pair_odd_round(self):
        self.pair_even_round()
        
    def pair_even_round(self):
        sorted_brackets_keys = sorted(self.brackets, reverse=True)
        highest_group = sorted_brackets_keys[0]
        lowest_group = sorted_brackets_keys[-1:]
        downfloaters = []

        for group_score in sorted_brackets_keys:
            group = self.brackets[group_score]
            if len(downfloaters) > 0:
                # TODO: B.5, B.6
                group[0:0] = downfloaters
                
                
            downfloaters = []
            for player in group:
                if 'pair' in player and player['pair']:
                    continue
                
                opponents = self.find_possible_opponents(player, group)
#                if group_score == 1.5:
#                    print(opponents)

                # C.1: B.1, B.2
                if len(opponents) == 0:
                    player['downfloater'] = True
                    downfloaters.append(player)
                elif len(opponents) == 1:
                    if 'downfloater' in player and player['downfloater']:
                        opponents[0]['upfloater'] = True
                    playerW, playerB = self.return_with_color_preferences(player, opponents[0])
                    self.pairs.append([playerW, playerB])
                    playerW['pair'] = True
                    playerB['pair'] = True
                elif len(opponents) > 1 and 'downfloater' in player and player['downfloater']:
                    sorted_players = self.order_players(opponents)
                    sorted_players[0]['upfloater'] = True
                    playerW, playerB = self.return_with_color_preferences(player, sorted_players[0])
                    self.pairs.append([playerW, playerB])
                    playerW['pair'] = True
                    playerB['pair'] = True
                    pass
                    
            without_opponents = [pl for pl in group if 'pair' not in pl or pl['pair'] is False]
            if len(without_opponents) > 2:
                self.pair_group_with_transposition(without_opponents)
                without_opponents = [pl for pl in group if 'pair' not in pl or pl['pair'] is False]
                if len(without_opponents) == 1:
                    without_opponents[0]['downfloater'] = True
                    downfloaters.append(without_opponents[0])
            
            if len(downfloaters) > 0 and lowest_group == group_score:
                pass
        pass
    
    # D 1.1 Homogenius transposition
    def pair_group_with_transposition(self, group):
        sorted_players = self.order_players(group)
        S1count = len(sorted_players) // 2
        S2count = len(sorted_players) - S1count
        S1 = sorted_players[:S1count]
        S2 = sorted_players[S1count:]

        def transposition(k,n):
            if k == n:
                yield S2
            else:
                for i in range(k, n):
                    if i != k:
                        S2[k], S2[i] = S2[i], S2[k]
                    for x in transposition(k+1, n):
                        yield x
                    if i != k:
                        S2[k], S2[i] = S2[i], S2[k]
            pass

        # Check simple pairing
        for S2 in transposition(0, S2count):
            problems = 0
            for index in range(S1count):
                if S2[index] not in self.find_possible_opponents(S1[index], group):
                    problems += 1
                    break
                    
            if problems > 0:
                continue
            
            # Pairing
            for index in range(S1count):
                playerW, playerB = self.return_with_color_preferences(S1[index], S2[index])
                self.pairs.append([playerW, playerB])
                playerW['pair'] = True
                playerB['pair'] = True
                
            return group
                
        return group
    
    def return_with_color_preferences(self, playerA, playerB):
        player1, player2 = self.order_players([playerA, playerB])
        player1_pref = self.get_color_preferences(player1)
        player2_pref = self.get_color_preferences(player2)
        player1_switched_color = self.get_switched_color_for_latest_game(player1)
        player2_switched_color = self.get_switched_color_for_latest_game(player2)
        
        if player1_pref <= -2 or player2_pref >= 2:
            return player1, player2
        elif player1_pref == -1 or player2_pref == 1:
            return player1, player2
        elif player1_pref >= 2 or player2_pref <= -2:
            return player2, player1
        elif player1_pref == 1 or player2_pref == -1:
            return player2, player1
        elif player1_switched_color and player1_switched_color == 'W':
            return player1, player2
        elif player2_switched_color and player2_switched_color == 'W':
            return player2, player1
        
        return player1, player2
    
    def find_player_by_name(self, name):
        for player in self.players:
            if player['name'] == name:
                return player
        return None

    # B.1, B.2    
    def find_possible_opponents(self, current_player, group, skip_color_pref = False):
        rest = []
        
        for player in group:
            if current_player != player :
                if 'pair' not in player or player['pair'] is False:
                    if player['name'] not in current_player['opponents'] : 
                        rest.append(player)

        if len(rest) == 0:
            return []
        
        # B.2
        # TODO: Top scored players
        color_pref = self.get_color_preferences(current_player)
        if abs(color_pref) >= 2 and skip_color_pref is False:
            for player in rest:
                opponent_color_pref = self.get_color_preferences(player)
                if opponent_color_pref == color_pref:
                    rest.remove(player)
                    continue
                 
        return rest
    
    def get_color_preferences(self, player):
        return 0

    def get_switched_color_for_latest_game(self, player):
        return None
    

class DbPairing(Pairing):
    ''' Pairing from tournament results stored in a Database '''
    
    def __init__(self, next_round=1):
        ''' players - list of dicts(name, rating, spread)
        games - list of dicts(round, player(name), opponent(name||None), 
                player_score, opponent_score, player_color, opponent_color, is_walkover)
        round_number - number of next round
        '''
        self.pairs = []
        rnd = TournamentRound.objects.get(round_no=next_round)
        self.tournament = rnd.tournament
        self.next_round = next_round
        self.players = []
        qs = Result.objects.exclude(first__name='Bye'
            ).filter(round__round_no__lt=next_round
            ).select_related('first','second','round')

        players = Participant.objects.select_related().filter(tournament_id=self.tournament
                    ).exclude(offed=True).order_by('round_wins','-game_wins','-spread')
        for pl in players:
            opponents = []
            spread = 0
            wins = 0
               
            if pl.name != 'Bye':
                games = qs.filter( Q(first=pl) | Q(second=pl)).order_by('-round')
                opponents = []
                for game in games:
                    if game.first.id == pl.id:
                        opponents.append(game.second)
                    else:
                        opponents.append(game.first)

                self.players.append( 
                     { 'name': pl.name,
                       'spread' : pl.spread,
                       'rating' : pl.seed,
                       'player' : pl,
                       'game_wins': pl.game_wins,
                       'score'  : pl.round_wins,
                       'opponents' : opponents
                     }
                )

        self.next_round = next_round

        
        # A.3
        brackets = {}
        for player in self.players:
            if player['score'] not in brackets:
                brackets[player['score']] = []
            brackets[player['score']].append(player)
        self.brackets = brackets

    def save(self):
        for pair in self.pairs:
            Result.objects.create(round_id=self.next_round,
                first=pair[0]['player'], second=pair[1]['player'])
        