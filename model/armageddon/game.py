import os
import struct

class HedEntry:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

class Game:
    def __init__(self, game_directory):
        self.directory = game_directory
        # TODO: filter by file exension
        with open(self.data_file('.hed'), 'rb') as hed_file:
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

        # TODO: filter by file exension
        self.data = open(self.data_file('.mfp'), 'rb')

    def close(self):
        self.data.close()

    @classmethod
    def hed_file(cls):
        return next(file for file in cls.data_files() if file.lower().endswith('.hed'))

    def data_file(self, extension):
        filename = next(file for file in self.data_files() if file.lower().endswith(extension))
        return os.path.join(self.directory, filename)

    @classmethod
    def data_files(cls):
        return [
            'Armageddon.HED',
            'Armageddon.MFP',
        ]

    def read_file(self, filename):
        entry = self.data.entries[filename]
        self.data.seek(entry.offset)
        return self.data.read(entry.length)

    def process_game_scenarios(self):
        return []
