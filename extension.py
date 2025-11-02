import random
import statistics as stats
#-------------------------------------
class Datas:
    def __init__(self):
        self.lvl1_actions = ["repos", "attaque", "parade", "attaque surprise", "developpement"]
        self.lvl2_actions = ["sieste", "fuite", "attaque en force", "developpement special"]
        self.lvl3_actions = ["sommeil reparateur", "attaque preparee", "technique de l'ancien", "PHS", "espionnage", "sabotage"]

        self.actions_effects = {
            "repos": {"mun": 1},
            "attaque": {"mun": -2, "attaque": 1},
            "parade": {"protection": 1},
            "attaque surprise": {"mun": -5, "attaque": 2},
            "developpement": {"dev": 1},
            "sieste": {"mun": 2},
            "fuite": {"protection": 2},
            "attaque en force": {"mun": -8, "attaque": 3},
            "developpement special": {"mun": 1, "dev": 1, "protection": 1},
            "sommeil reparateur": {"mun": 1, "protection": 2},
            "attaque preparee": {"attaque": 1, "protection": 1},
            "technique de l'ancien": {"mun": -4, "attaque": 2, "protection": 2},
            "PHS": {"mun": -2, "protection": 3},
            "espionnage": {"mun": -2, "espionnage": True},
            "sabotage": {"mun": -1, "sabotage": True}
        }
#-------------------------------------
class Game:
    def __init__(self, num_of_games, datas, analyse):
        self.playerA = None
        self.playerB = None
        self.winner = None
        self.loser = None
        self.num_of_games = num_of_games

    def reset(self):
        self.playerA = Player("playerA", datas, analyse)
        self.playerB = Player("playerB", datas, analyse)
        analyse.turn_per_game.append(0)
        analyse.esp_sab_per_game.append(0)

    def play(self, count):
        for i in range(count):
            self.reset()
            while self.playerA.hp > 0 and self.playerB.hp > 0:
                analyse.turn_per_game[-1] += 1

                self.playerA.attaque, self.playerA.protection = 0, 0
                self.playerB.attaque, self.playerB.protection = 0, 0

                self.applyEffect(self.playerA, self.playerA.chooseCard(self))
                self.applyEffect(self.playerB, self.playerB.chooseCard(self))

                self.attaqueResolve()

            self.winner = self.determineWinner()[0]
            self.loser = self.determineWinner()[1]
            analyse.analyseGame(self.winner, self.loser)

    def applyEffect(self, player, effect):
        player.mun += datas.actions_effects.get(effect, {}).get("mun", 0)
        player.dev += datas.actions_effects.get(effect, {}).get("dev", 0)
        player.attaque = datas.actions_effects.get(effect, {}).get("attaque", 0)
        player.protection = datas.actions_effects.get(effect, {}).get("protection", 0)
        if datas.actions_effects.get(effect, {}).get("espionnage", False):
            analyse.esp_sab_per_game[-1] += 1
        elif datas.actions_effects.get(effect, {}).get("sabotage", False):
            analyse.esp_sab_per_game[-1] += 1

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
        self.attaque = 0
        self.protection = 0
        self.possibles_actions = list(datas.lvl1_actions)
        self.temp_possibles_actions = list(self.possibles_actions)
        self.played_cards = {key: 0 for key in (datas.lvl1_actions + datas.lvl2_actions + datas.lvl3_actions)}
        self.two_last_cards_used = [None, None]

    @property
    def dev(self):
        return self._dev

    @dev.setter
    def dev(self, value):
        self._dev = value
        if self.dev >= 4 and analyse.turn_per_game[-1] >= 6 and self.level == 1:
            self.level = 2
            self.possibles_actions += datas.lvl2_actions
            self.possibles_actions = [action for action in self.possibles_actions if action not in ["parade", "repos", "developpement"]]
        elif self.dev >= 8 and analyse.turn_per_game[-1] >= 14 and self.level == 2:
            self.level = 3
            self.possibles_actions += datas.lvl3_actions
            self.possibles_actions = [action for action in self.possibles_actions if action not in ["fuite", "attaque"]]

    def chooseCard(self, game):
        self.temp_possibles_actions = [action for action in self.possibles_actions if not(action == self.two_last_cards_used[0] and action == self.two_last_cards_used[1])]
        for action in self.temp_possibles_actions:
            if self.mun + datas.actions_effects.get(action, {}).get("mun", 0) < 0:
                self.temp_possibles_actions = [card for card in self.temp_possibles_actions if card not in [action]]
        chosen_card = random.choice(self.temp_possibles_actions)
        self.played_cards[chosen_card] += 1
        self.two_last_cards_used[0] = self.two_last_cards_used[1]
        self.two_last_cards_used[1] = chosen_card
        return chosen_card
#-------------------------------------
class Analyse:
    def __init__(self, num_of_games):
        self.num_of_games = num_of_games

        self.games_won_by_playerA = 0
        self.games_won_by_playerB = 0
        self.draws = 0
        self.turn_per_game = []
        self.esp_sab_per_game = []

        self.cards_strength = {key: 0 for key in datas.actions_effects}
        self.bad_cards = {key: 0 for key in datas.actions_effects}

        self._classement = {key: (self.cards_strength[key] - self.bad_cards[key]) for key in self.cards_strength}

    @property
    def classement(self):
        dictionnary = {key: (self.cards_strength[key] - self.bad_cards[key]) for key in self.cards_strength}
        #return sorted(dictionnary.values())
        return dict(sorted(dictionnary.items(), key=lambda item: item[1]))

    @classement.setter
    def classement(self, value):
        self._classement = value

    def analyseGame(self, winner, loser):
        if winner == "draw":
            self.draws += 1
        elif winner.name == "playerB":
            self.games_won_by_playerB += 1
        elif winner.name == "playerA":
            self.games_won_by_playerA += 1

        if winner != "draw":
            for key in winner.played_cards:
                self.cards_strength[key] += winner.played_cards[key]
            for key in loser.played_cards:
                self.bad_cards[key] += loser.played_cards[key]

    def printRes(self, num_of_games):
        accuracy = len(str(num_of_games)) -1
        print("\n----------------------------------------\n")
        print(f"Sur {num_of_games} parties: ")
        print()
        print("Égalités: ", round(self.draws/self.num_of_games*100, accuracy), "%")
        print(f"Nombre de tours par partie moyen: {round(stats.mean(self.turn_per_game), accuracy)}, min: {min(self.turn_per_game)}, max: {max(self.turn_per_game)}")
        print("Nombre d'action espionnage ou sabotage par partie moyen: ", round(stats.mean(self.esp_sab_per_game), accuracy))
        print()
        for card in self.classement:
            print(f"Force de {card}: {round(self.classement[card]/self.num_of_games*50+50, accuracy)}%")
#-------------------------------------
num_of_games = 100000
datas = Datas()
analyse = Analyse(num_of_games)
game = Game(num_of_games, datas, analyse)
game.play(num_of_games)
analyse.printRes(num_of_games)