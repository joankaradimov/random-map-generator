import os
import re
import struct

import game
import armageddon.scenario

class MfpArchive:
    def __init__(self, file_path):
        hed_file_path = re.sub('.mfp$', '.hed', file_path.lower())
        with open(hed_file_path, 'rb') as hed_file:
            hed_data = hed_file.read()

        unknown, entry_count = struct.unpack_from('II', hed_data, 0)

        self.entries = {}
        for i in range(entry_count):
            offset = 72 * i + 8
            file_offset = struct.unpack_from('I', hed_data, offset)[0]
            file_length = struct.unpack_from('I', hed_data, offset + 68)[0]
            filename_length = hed_data[offset + 67]
            filename = hed_data[offset + 4: offset + filename_length + 4].decode('EUC-KR')

            self.entries[filename] = HedEntry(file_offset, file_length)

        self.file = open(file_path, 'rb')

    def close(self):
        self.file.close()

    def read_file(self, filename):
        entry = self.entries[filename]
        self.file.seek(entry.offset)
        return self.file.read(entry.length)

    def __contains__(self, filename):
        return filename in self.entries

class HedEntry:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

class Game(game.Game):
    def load_data_file(self, data_file):
        if hasattr(self, 'data'):
            # TODO: handle multiple data files
            raise Exception('Cannot handle multiple MFP files')

        self.data = MfpArchive(os.path.join(self.directory, data_file))

    def close(self):
        self.data.close()

    @classmethod
    def data_files(cls):
        return ['Armageddon.MFP']

    def scenario_filenames(self):
        return [x for x in self.data.entries if x.endswith('.amm')]

    def scenario_buider(self, filename, file):
        return armageddon.scenario.ScenarioBuilder(self, filename, file)

    def tileset_basename(self, tileset):
        return {
            self.tileset.BUILDINGS: 'Data\\buildings',
            self.tileset.DESERT: 'tileset\\Desert',
            self.tileset.EAD: 'tileset\\ead',
            self.tileset.EARTH: 'tileset\\Earth',
            self.tileset.SPACE: 'tileset\\space',
        }[tileset]
