import mpq
import os

from tileset import *
from scenario import *
from string_table import *
import game

class Game(game.Game):
    def __init__(self, game_directory):
        super().__init__(game_directory)

        self.data.add_archive(os.path.join(game_directory, 'Starcraft.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'Broodwar.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'StarDat.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'BrooDat.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'patch_rt.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'patch_ed.mpq'))

        self.tileset = Tileset

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
        return Scenario.builder(self, filename, chk_file)
