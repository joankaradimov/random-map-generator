import os
import re
import struct

import game

class HedEntry:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

class Game(game.Game):
    def load_data_file(self, data_file):
        if hasattr(self, 'data'):
            # TODO: handle multiple data files
            raise Exception('Cannot handle multiple MFP files')

        hed_filename = re.sub('.mfp$', '.hed', data_file.lower())
        with open(os.path.join(self.directory, hed_filename), 'rb') as hed_file:
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

        self.data = open(os.path.join(self.directory, data_file), 'rb')

    def close(self):
        self.data.close()

    @classmethod
    def data_files(cls):
        return ['Armageddon.MFP']

    def read_file(self, filename):
        entry = self.entries[filename]
        self.seek(entry.offset)
        return self.read(entry.length)

    def scenario_filenames(self):
        return [x for x in self.entries if x.endswith('.amm')]
