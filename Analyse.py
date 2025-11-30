class Analyse:
    def __init__(self, num_of_games):
        self.num_of_games = num_of_games
        self.games_won_by_playerA = 0
        self.games_won_by_playerB = 0
        self.draws = 0
        self.turn_per_game = []
        self.esp_sab = []
        self.winner_cards = {key: 0 for key in datas.actions_effects}
        self.loser_cards = {key: 0 for key on datas.actions_effects}
        self._win_rate = {key: (self.winner_cards[key] - self.loser_cards[key]) for key in self.winner_cards}
    
    @porperty
    def win_rate(self):
        w = self.einner_cards
        l = self.loser_cards
        rates = {}
        for key in w:
            total = w[key] + l[key]
            if total == 0:
                rates[key] = None
            else:
                rates[key] = w[key] / total
        return dict(sorted(rates.items(), key=lambda item: (item[1] is None, -(item[1] or 0)), reverse = True))

    @win_rate.setter
    def win_rate(self, value):
        self._win_rate = value

    def analyseGame(self, winner, loser):
        if winner = "draw":
            self.draws += 1
        elif winner.name = "playerA":
            self.games_won_by_playerA += 1
        elif winner.name = "playerB":
            self.games_won_by_playerB += 1
        
        if winner != "draw":
            for key in winner.played_cards:
                self.winner_cards[key] += winner.played_cards[key]
            for key in loser.played_cards:
                self.loser_cards[key] += loser.played_cards[key]
    
    def printRes(self, num_of_games):
        accuracy = len(str(self.num_of_games)) -1
        draws_per_game = round(self.draws / self.num_of_games * 100, accuracy)
        nbr_tour_moy = round(stats.mean(self.turn_per_game), accuracy)
        nbr_tour_min = min(self.turn_per_game)
        nbr_tour_max = max(self.turn_per_game)
        esp_sab_per_game = round(stats.mean(self.esp_sab), accuracy)
        print("\n----------------------------------------\n")
        print("Sur", self.num_of_games, "parties")
        print()
        print("Égalités: ", draws_per_game, "% des parties")
        print("Nombre de tour par partie moyen: ", nbr_tour_moy, "min: ", nbr_tour_min, "max: ", nbr_tour_max)
        print("Actions espionnage et sabotage en moyenne par partie: ", esp_sab_per_game)
        print("\nWinrate des cartes: ")
        for card, rate in self.win_rate.items():
            if rate is None:
                winrate = "-"
            else:
                rate = round(rate * 100, accuracy)
            print(f"Winrate {card}:{(16-len(card) * " ")}{winrate:.{accuracy}f}%")