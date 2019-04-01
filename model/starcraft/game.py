import mpq
import os

from tileset import *
import starcraft.scenario
from string_table import *
import game

class PlayerType(game.PlayerType):
    INACTIVE = 0
    RESCUE_PASSIVE = 3
    UNUSED = 4
    COMPUTER = 5
    HUMAN = 6
    NEUTRAL = 7

class Game(game.Game):
    def __init__(self, game_directory):
        super().__init__(game_directory)

        self.tileset = Tileset
        self.player_type = PlayerType

    @classmethod
    def data_files(cls):
        return [
            'Starcraft.mpq',
            'Broodwar.mpq',
            'StarDat.mpq',
            'BrooDat.mpq',
            'patch_rt.mpq',
            'patch_ed.mpq',
        ]

    def process_file(self, filename, file_path):
        if filename.endswith('.chk'):
            with open(file_path, 'rb') as chk_file:
                return self.process_chk(filename, chk_file)
        elif filename.endswith('.scm') or filename.endswith('.scx'):
            map = mpq.MPQFile(file_path)
            try:
                chk_file = map.open('staredit\\scenario.chk')
                return self.process_chk(filename, chk_file)
            finally:
                chk_file.close()
        else:
            return []

    def process_mpq(self):
        scenarios = []
        map_data = self.data.open('arr\mapdata.tbl')
        try:
            chk_files = StringTable(map_data)
        except mpq.storm.error as e:
            return scenarios
        finally:
            map_data.close()

        for filename in chk_files:
            chk_file = None
            try:
                file_path = filename + '\\staredit\\scenario.chk'
                if file_path in self.data:
                    chk_file = self.data.open(file_path)
                    scenarios += self.process_chk(os.path.basename(filename), chk_file)
            finally:
                if chk_file != None:
                    chk_file.close()

        return scenarios

    def scenario_buider(self, filename, chk_file):
        return starcraft.scenario.ScenarioBuilder(self, filename, chk_file)
