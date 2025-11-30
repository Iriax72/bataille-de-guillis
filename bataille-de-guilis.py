import random
import statistics as stats
import Analyse from "./Analyse.py"
#-------------------------------------
class Datas:
    def __init__(self):
        self.lvl1_actions = ["repos", "attaque", "parade", "att-surprise", "dev"]
        self.lvl2_actions = ["sieste", "fuite", "att-en-force", "dev-special"]
        self.lvl3_actions = ["sommeil-repa...", "att-preparee", "tech-de-l'ancien", "PHS", "espionnage", "sabotage"]

        self.actions_effects = {
            "repos": {"mun": 1},
            "attaque": {"mun": -2, "attaque": 1},
            "parade": {"protection": 1},
            "att-surprise": {"mun": -5, "attaque": 2},
            "dev": {"dev": 1},
            "sieste": {"mun": 2},
            "fuite": {"protection": 2},
            "att-en-force": {"mun": -8, "attaque": 3},
            "dev-special": {"mun": 1, "dev": 1, "protection": 1},
            "sommeil-repa...": {"mun": 1, "protection": 2},
            "att-preparee": {"attaque": 1, "protection": 1},
            "tech-de-l'ancien": {"mun": -4, "attaque": 2, "protection": 2},
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
        analyse.esp_sab.append(0)

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
            analyse.esp_sab[-1] += 1
        elif datas.actions_effects.get(effect, {}).get("sabotage", False):
            analyse.esp_sab[-1] += 1

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
            self.possibles_actions = [action for action in self.possibles_actions if action not in ["parade", "repos", "dev"]]
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
num_of_games = 10000
datas = Datas()
analyse = Analyse()
game = Game(num_of_games, datas, analyse)
game.play(num_of_games)
analyse.printRes(num_of_games)