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
                scenarios += self.process_file(filename, file_path)

        return scenarios

    def process_chk(self, filename, chk_file):
        try:
            return [self.scenario_buider(filename, chk_file).to_scenario()]
        except Exception as e:
            return []
