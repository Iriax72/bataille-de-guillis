import random
import statistics as stats
#-------------------------------------
class Datas:
    def __init__(self):
        self.lvl1_actions = ["repos", "attaque", "parade", "att-surprise", "dev", "emploi", "entrainement"]
        self.lvl2_actions = ["sieste", "fuite", "att-en-force", "dev-special", "travail-acharne", "entrainement-intensif"]
        self.lvl3_actions = ["sommeil-repa...", "att-preparee", "tech-de-l'ancien", "PHS", "espionnage", "sabotage", "buisness"]

        self.actions_effects = {
            "repos": {"mun": 1},
            "attaque": {"mun": -2, "attaque": 1},
            "parade": {"protection": 1},
            "att-surprise": {"mun": -5, "attaque": 2},
            "dev": {"dev": 1},
            "emploi": {"gold": 1},
            "entrainement": {"amelioration": True},
            "sieste": {"mun": 2},
            "fuite": {"protection": 2},
            "att-en-force": {"mun": -8, "attaque": 3},
            "dev-special": {"mun": 1, "dev": 1, "protection": 1},
            "travail-acharne": {"mun": -5, "gold": 4},
            "entrainement-intensif": {"mun": 1, "protection": 1, "amelioration": True},
            "sommeil-repa...": {"mun": 1, "protection": 2},
            "att-preparee": {"attaque": 1, "protection": 1},
            "tech-de-l'ancien": {"mun": -4, "attaque": 2, "protection": 2},
            "PHS": {"mun": -2, "protection": 3},
            "espionnage": {"mun": -2, "espionnage": True},
            "sabotage": {"mun": -1, "sabotage": True},
            "buisness": {"gold": 2, "mun": 1, "protection": 1}
        }

        self.ameliorations = {
            "rechargement-rapide": {"mun": -4, "gold": -4},
            "dev-premature": {"mun": -4, "gold": -4},
            "coach-perso": {"mun": -4, "gold": -4},
            "protec-a-gogo": {"mun": -4, "gold": -4},
            "att-supreme": {"mun": -4, "gold": -4},
            "station-de-recup": {"mun": -4, "gold": -4},
            "booste": {"mun": -4, "gold": -4},
            "profiteur": {"mun": -4, "gold": -4},
            "combo": {"mun": -4, "gold": -4},
            "jaloux": {"mun": -4, "gold": -4},
            "chapardeur": {"mun": -4, "gold": -4},
            "tech-du-flemmard": {"mun": -4, "gold": -4}
        }
#-------------------------------------
class Game:
    def __init__(self, num_of_games, datas, analyse):
        self.playerA = None
        self.playerB = None
        self.winner = None
        self.loser = None
        self.num_of_games = num_of_games
        self.ameliorations = None

    def reset(self):
        self.playerA = Player("playerA", datas, analyse)
        self.playerB = Player("playerB", datas, analyse)
        analyse.turn_per_game.append(0)
        analyse.esp_sab_per_game.append(0)
        self.ameliorations = list(datas.ameliorations)
        while len(self.ameliorations) > 5:
            self.ameliorations.pop(random.randint(0, len(self.ameliorations)-1))

    def play(self, count):
        for partie in range(count):
            self.reset()
            while self.playerA.hp > 0 and self.playerB.hp > 0:
                analyse.turn_per_game[-1] += 1

                self.playerA.attaque, self.playerA.protection = 0, 0
                self.playerB.attaque, self.playerB.protection = 0, 0

                self.applyEffect(self.playerA, self.playerA.chooseCard(self, self.playerB), self.playerB)
                self.applyEffect(self.playerB, self.playerB.chooseCard(self, self.playerA), self.playerA)

                self.attaqueResolve()

            self.winner = self.determineWinner()[0]
            self.loser = self.determineWinner()[1]
            analyse.analyseGame(self.winner, self.loser)
            print(f"Fin de la partie {partie+1}")

    def applyEffect(self, player, effect, opponent):
        player.mun += datas.actions_effects.get(effect, {}).get("mun", 0)
        player.dev += datas.actions_effects.get(effect, {}).get("dev", 0)
        player.gold += datas.actions_effects.get(effect, {}).get("gold", 0)
        player.attaque = datas.actions_effects.get(effect, {}).get("attaque", 0)
        player.protection = datas.actions_effects.get(effect, {}).get("protection", 0)
        if datas.actions_effects.get(effect, {}).get("espionnage", False):
            analyse.esp_sab_per_game[-1] += 1
        elif datas.actions_effects.get(effect, {}).get("sabotage", False):
            analyse.esp_sab_per_game[-1] += 1
        if datas.actions_effects.get(effect, {}).get("amelioration", False):
            player.getAmelioration(opponent.ameliorations)

    def attaqueResolve(self):
        if self.playerA.attaque > self.playerB.protection:
            self.playerB.hp -= 1
            if analyse.turn_per_game[-1] > 39:
                self.playerB.hp -= 1
        if self.playerB.attaque > self.playerA.protection:
            self.playerA.hp -= 1
            if analyse.turn_per_game[-1] > 39:
                self.playerA.hp -= 1

    def determineWinner(self):
        if self.playerA.hp <= 0 and self.playerB.hp <= 0:
            return ("draw", None)
        elif self.playerA.hp <= 0:
            return (self.playerB, self.playerA)
        elif self.playerB.hp <= 0:
            return (self.playerA, self.playerB)
#-------------------------------------
class Player:
    def __init__(self, name, datas, analyse):
        self.name = name
        self.hp = 3
        self._dev = 0
        self.level = 1
        self.mun = 0
        self.gold = 0
        self.attaque = 0
        self.protection = 0
        self.possibles_actions = list(datas.lvl1_actions)
        self.temp_possibles_actions = list(self.possibles_actions)
        self.played_cards = {key: 0 for key in (datas.lvl1_actions + datas.lvl2_actions + datas.lvl3_actions)}
        self.two_last_cards_used = [None, None]
        self.ameliorations = []

    @property
    def dev(self):
        return self._dev

    @dev.setter
    def dev(self, value):
        self._dev = value
        if self.dev >= 4 and analyse.turn_per_game[-1] >= 6 and self.level == 1:
            self.level = 2
            self.possibles_actions += datas.lvl2_actions
            self.possibles_actions = [action for action in self.possibles_actions if action not in ["parade", "repos", "dev", "entrainement"]]
        elif self.dev >= 8 and analyse.turn_per_game[-1] >= 14 and self.level == 2:
            self.level = 3
            self.possibles_actions += datas.lvl3_actions
            self.possibles_actions = [action for action in self.possibles_actions if action not in ["fuite", "attaque", "emploi"]]

    def chooseCard(self, game, opponent): # il y a pas besoin de game
        # Start from possible actions but avoid repeating the same two last cards
        candidates = [action for action in self.possibles_actions if not (action == self.two_last_cards_used[0] and action == self.two_last_cards_used[1])]

        # 1) Filter out actions that would make mun negative
        candidates = [a for a in candidates if self.mun + datas.actions_effects.get(a, {}).get("mun", 0) >= 0]

        # 2) For actions that grant an amelioration, ensure there's at least one purchasable amelioration
        filtered = []
        for a in candidates:
            if datas.actions_effects.get(a, {}).get("amelioration", False):
                # find ameliorations available in this game that neither player has and that the player can afford
                possible_amelios = []
                for amelio in game.ameliorations:
                    if amelio in self.ameliorations:
                        continue
                    if amelio in opponent.ameliorations:
                        continue
                    cost_gold = datas.ameliorations.get(amelio, {}).get("gold", 0)
                    cost_mun = datas.ameliorations.get(amelio, {}).get("mun", 0)
                    # costs in datas are negative values (ex: -4), so after applying them the resource must stay >= 0
                    if self.gold + cost_gold >= 0 and self.mun + cost_mun >= 0:
                        possible_amelios.append(amelio)
                if possible_amelios:
                    filtered.append(a)
                else:
                    # no purchasable amelioration -> don't include this action
                    continue
            else:
                filtered.append(a)

        # If nothing remains (very unlikely), fallback to a safe action: prefer 'repos' else any possible action
        if not filtered:
            if "repos" in self.possibles_actions:
                chosen_card = "repos"
            else:
                # last resort: ignore resource constraints and pick any allowed action
                fallback = [action for action in self.possibles_actions if not (action == self.two_last_cards_used[0] and action == self.two_last_cards_used[1])]
                if not fallback:
                    fallback = list(self.possibles_actions) or [None]
                chosen_card = random.choice(fallback)
        else:
            chosen_card = random.choice(filtered)
        self.played_cards[chosen_card] += 1
        self.two_last_cards_used[0] = self.two_last_cards_used[1]
        self.two_last_cards_used[1] = chosen_card
        return chosen_card
    
    def getAmelioration(self, opponent_amelio):
        possible_ameliorations = [amelio for amelio in game.ameliorations if amelio not in self.ameliorations and amelio not in opponent_amelio]
        possible_ameliorations = [amelio for amelio in possible_ameliorations if self.gold + datas.ameliorations.get(amelio, {}).get("gold", 0) >= 0 and self.mun + datas.ameliorations.get(amelio, {}).get("mun", 0) >= 0]
        if possible_ameliorations:
            new_amelio = random.choice(possible_ameliorations)
            self.ameliorations.append(new_amelio)
            self.gold += datas.ameliorations.get(new_amelio, {}).get("gold", 0)
            self.mun += datas.ameliorations.get(new_amelio, {}).get("mun", 0)
#-------------------------------------
class Analyse:
    def __init__(self, num_of_games):
        self.num_of_games = num_of_games

        self.games_won_by_playerA = 0
        self.games_won_by_playerB = 0
        self.draws = 0
        self.turn_per_game = []
        self.esp_sab_per_game = []

        self.winner_cards = {key: 0 for key in datas.actions_effects}
        self.loser_cards = {key: 0 for key in datas.actions_effects}

        self._win_rate = {key: (self.winner_cards[key] - self.loser_cards[key]) for key in self.winner_cards}

    @property
    def win_rate(self):
        w = self.winner_cards
        l = self.loser_cards
        rates = {}
        for key in w:
            total = w[key] + l[key]
            if total == 0:
                rates[key] = None
            else:
                rates[key] = w[key] / total
        return dict(sorted(rates.items(), key=lambda item: (item[1] is None, -(item[1] or 0)), reverse=True))

    @win_rate.setter
    def win_rate(self, value):
        self._win_rate = value

    def analyseGame(self, winner, loser):
        if winner == "draw":
            self.draws += 1
        elif winner.name == "playerB":
            self.games_won_by_playerB += 1
        elif winner.name == "playerA":
            self.games_won_by_playerA += 1

        if winner != "draw":
            for key in winner.played_cards:
                self.winner_cards[key] += winner.played_cards[key]
            for key in loser.played_cards:
                self.loser_cards[key] += loser.played_cards[key]

    def printRes(self, num_of_games):
        accuracy = len(str(num_of_games)) -1
        print("\n----------------------------------------\n")
        print(f"Sur {num_of_games} parties: ")
        print("\nÉgalités: ", round(self.draws/self.num_of_games*100, accuracy), "%")
        print(f"Nombre de tours par partie moyen: {round(stats.mean(self.turn_per_game), accuracy)}, min: {min(self.turn_per_game)}, max: {max(self.turn_per_game)}")
        print("Nombre d'action espionnage ou sabotage par partie moyen: ", round(stats.mean(self.esp_sab_per_game), accuracy))
        print("\n|Carte:                |Winrate:")
        print("|----------------------|----------")
        for card, rate in self.win_rate.items():
            if rate is None:
                winrate = "-"
            else:
                winrate = round(rate * 100, accuracy)
            print(f"|{card}{(22-len(card)) * " "}|{winrate:.{accuracy}f}%")
#-----------------------------------------------
num_of_games = 1000
datas = Datas()
analyse = Analyse(num_of_games)
game = Game(num_of_games, datas, analyse)
game.play(num_of_games)
analyse.printRes(num_of_games)