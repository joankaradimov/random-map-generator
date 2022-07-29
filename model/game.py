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
    def __new__(cls, game_directory):
        import armageddon
        import starcraft
        import warcraft
        import warcraft2

        games_types = [armageddon.Game, warcraft.Game, warcraft2.Game, starcraft.Game]
        for game in games_types:
            data_file_paths = (os.path.join(game_directory, x) for x in game.data_files())
            if all(os.path.exists(x) for x in data_file_paths):
                instance = super().__new__(game)
                return instance

        raise Exception('Could not detect game')

    def __init__(self, game_directory):
        self.directory = game_directory
        self._tiles_cache = {}

        for data_file in self.data_files():
            self.load_data_file(data_file)

    def close(self):
        self.data.close()

    def process_game_scenarios(self):
        scenarios = []
        scenarios += self.process_game_archive()
        scenarios += self.process_directory(os.path.join(self.directory, 'Maps'))
        return scenarios

    def process_game_archive(self):
        scenarios = []

        for filename in self.scenario_filenames():
            file = None
            try:
                if filename in self.data:
                    file = self.data.open(filename)
                    scenarios += self.process_chk(os.path.basename(filename), file)
            finally:
                if file != None:
                    file.close()

        return scenarios

    def process_directory(self, directory):
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

    def process_tileset_file(self, tileset, entry_type):
        file = None
        try:
            file = self.data.open(self.tileset_basename(tileset) + '.' + entry_type.EXTENSION)

            entries = []
            while file.tell() != file.size():
                data = file.read(entry_type.SIZE)
                entry = entry_type(data)
                entries.append(entry)

            return entries
        finally:
            if file != None:
                file.close()

class MpqBasedGame(Game):
    def __init__(self, game_directory):
        self.data = mpq.MPQFile()
        super().__init__(game_directory)

    def load_data_file(self, data_file):
        self.data.add_archive(os.path.join(self.directory, data_file))
