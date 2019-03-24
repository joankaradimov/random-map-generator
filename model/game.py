import mpq
import os

from tileset import *
from scenario import *
from string_table import *

class Game:
    def __init__(self, game_directory):
        self.directory = game_directory
        self.data = mpq.MPQFile()

        self.data.add_archive(os.path.join(game_directory, 'Starcraft.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'Broodwar.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'StarDat.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'BrooDat.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'patch_rt.mpq'))
        self.data.add_archive(os.path.join(game_directory, 'patch_ed.mpq'))

        self.tileset = Tileset

    def close(self):
        self.data.close()

    def process_game_scenarios(self):
        scenarios = []
        scenarios += self.process_mpq()
        scenarios += self.process_scenarios(os.path.join(self.directory, 'Maps'))
        return scenarios

    def process_scenarios(self, directory):
        scenarios = []

        for dir_name, subdir_list, file_list in os.walk(directory):
            for filename in file_list:
                file_path = os.path.join(dir_name, filename)
                if filename.endswith('.chk'):
                    with open(file_path, 'rb') as chk_file:
                        scenarios += self.process_chk(filename, chk_file)
                elif filename.endswith('.scm') or filename.endswith('.scx'):
                    scenarios += self.process_scenario(file_path)

        return scenarios

    def process_scenario(self, scenario_path):
        filename = os.path.basename(scenario_path)
        map = mpq.MPQFile(scenario_path)
        try:
            chk_file = map.open('staredit\\scenario.chk')
            return self.process_chk(filename, chk_file)
        finally:
            chk_file.close()

    def process_chk(self, filename, chk_file):
        try:
            return [Scenario.builder(self, filename, chk_file).to_scenario()]
        except Exception as e:
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
