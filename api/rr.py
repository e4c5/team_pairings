from api.pairing import Pairing

class RoundRobinPairing(Pairing):
    
    def __init__(self, rnd):
        super().__init__(rnd)

    def make_it(self):
        for _ in range(self.rnd.round_no):
            self.pairs = [self.pairs[0]] + [self.pairs[-1]] + self.pairs[1:-1]

        for i in range(len(self.players) // 2):
            player1 = self.players[i]
            player2 = self.players[len(self.players) - i - 1]
            self.pairs.append([player1, player2])

        return self.pairs    
            