# this code was imported from the react_pairing project
# it has been cut and chopped, some features that may seem to be missing
# might actually be there


from tournament.models import Participant, Result, TournamentRound
from django.db.models import Q
from api.pairing import Pairing

class SwissPairing(Pairing):
    '''
    Pairing procedure according to Swiss system rules

    Originally from: https://github.com/gnomeby/swiss-system-chess-tournament
    Adapted to work with scrabble scores rather than colors.
    '''

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

        self.find_brackets()

        if self.next_round == 1:
            self.pair_first_round()
        else:
            self.pair_other_round()
            required = len(self.players) // 2
            if self.bye:
                required += 1
            if len(self.pairs) < required:
                # the pairing was not completed. Collapse the first two brackets
                self.reset()
                sorted_brackets_keys = sorted(self.brackets, reverse=True)
                self.brackets[sorted_brackets_keys[0]].extend(self.brackets[sorted_brackets_keys[1]])
                self.brackets[sorted_brackets_keys[1]] = []
                
                self.pair_other_round()

                if len(self.pairs) < required:
                    self.reset()
                    # still no luck. Try pairing the last person first
                    last = len(self.players) -1
                    while last > 0:
                        lp = self.players[last]
                        if lp['pair'] or lp['name'] == 'Bye':
                            last -= 1
                        else:
                            break
                    
                    prev = last - 1
                    while prev >= 0:
                        opponent = self.players[prev]
                        if lp['name'] not in opponent['opponents']:
                            lp['pair'] = True
                            opponent['pair'] = True
                            self.pair_other_round()
                            self.pairs.append(self.return_with_color_preferences(lp, opponent))        
                            break
                        prev -= 1
                    
                    

        return self.pairs

    def reset(self):
        if self.bye:
            b = self.pairs[0]
            self.pairs = [b]
        else:
            self.pairs = []
        self.find_brackets()
        for player in self.players:
            player['pair'] = False
            player['downfloater'] = False

    def find_brackets(self):
        brackets = {}
        for player in self.players:
            if player['score'] not in brackets:
                brackets[player['score']] = []
            brackets[player['score']].append(player)
        self.brackets = brackets

    def pair_first_round(self):
        """Pairs the first round.
        At this point you should have forfeited all absent players and the bye
        should have been assigned."""
        sorted_players = self.order_players(self.players)
        S1count = len(self.players) // 2

        for index in range(S1count):
            self.pairs.append(
                [sorted_players[index], sorted_players[S1count+index]])

    def pair_other_round(self):
        """Pairs the second round onwards.
        At this point you should have forfeited all absent players and the bye
        should have been assigned."""

        sorted_brackets_keys = sorted(self.brackets, reverse=True)
        downfloaters = []

        for group_score in sorted_brackets_keys:
            group = self.brackets[group_score]
            if len(downfloaters) > 0:
                # TODO: B.5, B.6
                group[0:0] = downfloaters

            downfloaters = []
            for player in group:
                if player.get('pair'):
                    continue

                opponents = self.find_possible_opponents(player, group)

                # C.1: B.1, B.2
                if len(opponents) == 0:
                    player['downfloater'] = True
                    downfloaters.append(player)
                elif len(opponents) == 1:
                    if 'downfloater' in player and player['downfloater']:
                        opponents[0]['upfloater'] = True
                    playerW, playerB = self.return_with_color_preferences(
                        player, opponents[0])
                    self.pairs.append([playerW, playerB])
                    playerW['pair'] = True
                    playerB['pair'] = True
                elif len(opponents) > 1 and 'downfloater' in player and player['downfloater']:
                    sorted_players = opponents
                    sorted_players[0]['upfloater'] = True
                    playerW, playerB = self.return_with_color_preferences(
                        player, sorted_players[0])
                    self.pairs.append([playerW, playerB])
                    playerW['pair'] = True
                    playerB['pair'] = True

            without_opponents = [pl for pl in group if pl['pair'] is False]
            if len(without_opponents) > 2:
                self.pair_group_with_transposition(without_opponents)
                without_opponents = [pl for pl in group if pl['pair'] is False]
                if len(without_opponents) == 1:
                    without_opponents[0]['downfloater'] = True
                    downfloaters.append(without_opponents[0])
          

    # D 1.1 Homogenius transposition
    def pair_group_with_transposition(self, group):
        sorted_players = group
        S1count = len(sorted_players) // 2
        S2count = len(sorted_players) - S1count
        S1 = sorted_players[:S1count]
        S2 = sorted_players[S1count:]

        def transposition(k, n):
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
                playerW, playerB = self.return_with_color_preferences(
                    S1[index], S2[index])
                self.pairs.append([playerW, playerB])
                playerW['pair'] = True
                playerB['pair'] = True

            return group

        return group

   
    # B.1, B.2
    def find_possible_opponents(self, current_player, group):
        rest = []

        for player in group:
            if current_player != player:
                if player['pair'] is False:
                    if player['name'] not in current_player['opponents']:
                        rest.append(player)
                    else:
                        # already played lets find out if we are within the number
                        # of repeats that are allowed for this pair
                        if self.rnd.repeats:
                            count = 0
                            for opponent in current_player['opponents']:
                                if player['name'] == opponent:
                                    count += 1
                            
                            if count <= self.rnd.repeats:
                                rest.append(player)

        return rest

