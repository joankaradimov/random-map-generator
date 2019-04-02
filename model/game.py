import enum
import mpq
import os

from tileset import *
from scenario import *
from string_table import *

class PlayerType(enum.Enum):
    @property
    def is_active(self):
        return self == self.HUMAN or self == self.COMPUTER

class Game:
    def __init__(self, game_directory):
        self.directory = game_directory
        self.data = mpq.MPQFile()

        for data_file in self.data_files():
            self.load_data_file(data_file)

    def close(self):
        self.data.close()

    def load_data_file(self, data_file):
        self.data.add_archive(os.path.join(self.directory, data_file))

    def process_game_scenarios(self):
        scenarios = []
        scenarios += self.process_mpq()
        scenarios += self.process_scenarios(os.path.join(self.directory, 'Maps'))
        return scenarios

    def process_mpq(self):
        scenarios = []

        for filename in self.scenario_filenames():
            chk_file = None
            try:
                if filename in self.data:
                    chk_file = self.data.open(filename)
                    scenarios += self.process_chk(os.path.basename(filename), chk_file)
            finally:
                if chk_file != None:
                    chk_file.close()

        return scenarios

    def process_scenarios(self, directory):
        scenarios = []

        for dir_name, subdir_list, file_list in os.walk(directory):
            for filename in file_list:
                file_path = os.path.join(dir_name, filename)
                scenarios += self.process_file(filename, file_path)

        return scenarios

    def process_chk(self, filename, chk_file):
        try:
            return [self.scenario_buider(filename, chk_file).to_scenario()]
        except Exception as e:
            return []
