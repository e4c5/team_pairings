from api.pairing import Pairing

class RoundRobinPairing(Pairing):
    
    def __init__(self, rnd):
        super().__init__(rnd)

    def make_it(self):
        if self.rnd.round_no > 1:
            n = self.rnd.round_no
            self.players = self.players[-n:] + self.players[:-n]

        for i in range(len(self.players) // 2):
            player1 = self.players[i]
            player2 = self.players[len(self.players) - i - 1]
            self.pairs.append([player1, player2])

        return self.pairs    
            