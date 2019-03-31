import os

import warcraft2.scenario
import warcraft2.tileset
import game

class PlayerType(game.PlayerType):
    _PASSIVE_COMPUTER = 0
    _COMPUTER = 1
    PASSIVE_COMPUTER = 2
    NOBODY = 3
    COMPUTER = 4
    HUMAN = 5
    RESCUE_PASSIVE = 6
    RESCUE_ACTIVE = 7
    # 0x08 - 0xff are passive computer

class Game(game.Game):
    def __init__(self, game_directory):
        super().__init__(game_directory)

        self.data.add_archive(os.path.join(game_directory, 'War2Dat.mpq'))

        self.tileset = warcraft2.tileset.Tileset
        self.player_type = PlayerType

    def process_file(self, filename, file_path):
        if filename.endswith('.pud'):
            with open(file_path, 'rb') as chk_file:
                return self.process_chk(filename, chk_file)
        else:
            return []

    def process_mpq(self):
        return [] # TODO: implement

    def scenario_buider(self, filename, chk_file):
        return warcraft2.scenario.ScenarioBuilder(self, filename, chk_file)
