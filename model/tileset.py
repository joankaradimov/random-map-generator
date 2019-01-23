import mpq
import enum
import numpy
import os
import struct

import config

class CV5Entry:
    SIZE = 52
    EXTENSION = 'cv5'

    def __init__(self, data):
        self.data = struct.unpack('HBBHHHHHHHH', data[: 20])
        self.megatiles = struct.unpack('H' * 16, data[20:])

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
    __slots__ = 'minitiles', 'buildable'

    def __init__(self, megatile_index, cv5_entry, vf4_entries, vx4_entries):
        megatile = cv5_entry.megatiles[megatile_index]
        minitiles = [Minitile(vf4_entries[megatile].data[i], vx4_entries[megatile].data[i]) for i in range(16)]
        self.minitiles = numpy.array(minitiles, dtype=object).reshape(4, 4)
        self.buildable = not bool((cv5_entry.data[1] >> 4) & 8)

class Minitile:
    __slots__ = 'walkable', 'height', 'blocks_view', 'ramp', 'graphics_id', 'graphics_flipped'

    def __init__(self, vf4_entry, vx4_entry):
        self.walkable = bool(vf4_entry & 1)
        self.height = (vf4_entry >> 1) & 3
        self.blocks_view = bool(vf4_entry & 8)
        self.ramp = bool(vf4_entry & 16)
        self.graphics_id = vx4_entry >> 1
        self.graphics_flipped = bool(vx4_entry & 1)

class Tileset(enum.Enum):
    BADLANDS = 0
    SPACE_PLATFORM = 1
    INSTALLATION = 2
    ASHWORLD = 3
    JUNGLE = 4
    DESERT = 5
    ARCTIC = 6
    TWILIGHT = 7

    def __init__(self, value):
        self.__tiles_cache = None

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
        if self.__tiles_cache == None:
            mpq_file = mpq.MPQFile(os.path.join(config.STARCRAFT_ROOT, self.mpq_filename))
            cv5_entries = self.process(mpq_file, CV5Entry)
            vf4_entries = self.process(mpq_file, VF4Entry)
            vx4_entries = self.process(mpq_file, VX4Entry)

            self.__tiles_cache = []
            for cv5_entry in cv5_entries:
                for i, megatile in enumerate(cv5_entry.megatiles):
                    self.__tiles_cache.append(Tile(i, cv5_entry, vf4_entries, vx4_entries))

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
