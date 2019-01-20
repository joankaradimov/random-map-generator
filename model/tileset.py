import mpq
import enum
import os
import struct

import config

class CV5Entry:
    SIZE = 52
    EXTENSION = 'cv5'

    def __init__(self, data):
        self.data = struct.unpack('HHHHHHHHHH', data[: 20])
        self.minitiles = struct.unpack('H' * 16, data[20:])

class VF4Entry:
    SIZE = 32
    EXTENSION = 'vf4'

    def __init__(self, data):
        self.data = struct.unpack('H' * 16, data)

class VX4Entry:
    SIZE = 32
    EXTENSION = 'vx4'

    def __init__(self, data):
        self.data = struct.unpack('H' * 16, data)

class Tile:
    def __init__(self, cv5_entry, vf4_entries, vx4_entries):
        pass

class Tileset(enum.Enum):
    BADLANDS = 0
    SPACE_PLATFORM = 1
    INSTALLATION = 2
    ASHWORLD = 3
    JUNGLE = 4
    DESERT = 5
    ARCTIC = 6
    TWILIGHT = 7

    @property
    def mpq_filename(self):
        if self.value < 5:
            return 'StarDat.mpq'
        else:
            return 'BrooDat.mpq'

    @property
    def tileset_filename(self):
        return {
            self.BADLANDS: 'badlands',
            self.SPACE_PLATFORM: 'platform',
            self.INSTALLATION: 'install',
            self.ASHWORLD: 'ashworld',
            self.JUNGLE: 'jungle',
            self.DESERT: 'Desert',
            self.ARCTIC: 'Ice',
            self.TWILIGHT: 'Twilight',
        }[self]

    @property
    def tiles(self):
        if not hasattr(self, '__tiles_cache'):
            mpq_file = mpq.MPQFile(os.path.join(config.STARCRAFT_ROOT, self.mpq_filename))
            cv5_entries = self.process(mpq_file, CV5Entry)
            vf4_entries = self.process(mpq_file, VF4Entry)
            vx4_entries = self.process(mpq_file, VX4Entry)

            self.__tiles_cache = [Tile(cv5, vf4_entries, vx4_entries) for cv5 in cv5_entries]

        return self.__tiles_cache

    def process(self, mpq_file, entry_type):
        try:
            file = mpq_file.open(os.path.join('tileset', self.tileset_filename + '.' + entry_type.EXTENSION))

            entries = []
            while file.tell() != file.size():
                data = file.read(entry_type.SIZE)
                entry = entry_type(data)
                entries.append(entry)

            return entries
        finally:
            file.close()
