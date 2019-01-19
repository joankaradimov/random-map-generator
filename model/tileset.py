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
            return 'BroodDat.mpq'

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

    def load_data(self):
        self.cv5_entries = self.process(CV5Entry)
        self.vf4_entries = self.process(VF4Entry)
        self.vx4_entries = self.process(VX4Entry)

    def process(self, entry_type):
        mpq_file = mpq.MPQFile(os.path.join(config.STARCRAFT_ROOT, self.mpq_filename))
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
