import enum
import numpy
import os
import struct

import config
import graphics

class CV5Entry:
    SIZE = 52
    EXTENSION = 'cv5'

    def __init__(self, data):
        self.data = struct.unpack_from('HBBHHHHHHHH', data)
        self.megatiles = struct.unpack_from('H' * 16, data, offset=20)

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

class VR4Entry:
    SIZE = 64
    EXTENSION = 'vr4'

    def __init__(self, data):
        self.data = struct.unpack('B' * self.SIZE, data)

    def to_graphics(self, wpe_entries):
        return numpy.stack([wpe_entries[x].data for x in self.data]).reshape([8, 8, 3])

class WPEEntry:
    SIZE = 4
    EXTENSION = 'wpe'

    def __init__(self, data):
        self.data = numpy.array(struct.unpack_from('BBB', data), dtype=numpy.uint8)

class Tile:
    __slots__ = 'group_offset', 'tile_group', 'minitiles'

    def __init__(self, tile_group, group_offset, vf4_entry, vx4_entry, minitile_graphics):
        self.group_offset = group_offset
        self.tile_group = tile_group

        minitiles = [Minitile(vf4_entry.data[i], vx4_entry.data[i], minitile_graphics) for i in range(16)]
        self.minitiles = numpy.array(minitiles, dtype=object).reshape(4, 4)

    @property
    def index(self):
        return self.group_id * 16 + self.group_offset

    @property
    def group_id(self):
        return self.tile_group.group_id

    @property
    def buildable(self):
        return self.tile_group.buildable

    @property
    def graphics(self):
        return graphics.tile(self.minitiles)

    @property
    def is_doodad(self):
        return self.tile_group.is_doodad

    @property
    def is_empty(self):
        return numpy.count_nonzero(numpy.vectorize(lambda x: x.graphics_id)(self.minitiles)) == 0

    def __repr__(self):
        return '<%s.%s - megagroup: %d, group %d, item %d>' % (
            type(self).__module__,
            type(self).__name__,
            self.tile_group.megagroup,
            self.group_id,
            self.group_offset)

    def __hash__(self):
        result = 0
        for _, minitile in numpy.ndenumerate(self.minitiles):
            result = result * 37 + hash(minitile)
        return result

    def __eq__(self, other):
        return self.buildable == other.buildable and numpy.array_equal(self.minitiles, other.minitiles)

class TileGroup:
    __slots__ = 'megagroup', 'group_id', 'buildable', '__dict__'

    def __init__(self, group_id, cv5_entry):
        self.megagroup = cv5_entry.data[0]
        self.group_id = group_id
        self.buildable = not bool((cv5_entry.data[1] >> 4) & 8)

        if self.is_doodad:
            self.overlay_id = cv5_entry.data[3]
        else:
            self.left_edge = cv5_entry.data[3]
            self.top_edge = cv5_entry.data[4]
            self.right_edge = cv5_entry.data[5]
            self.bottom_edge = cv5_entry.data[6]

    @property
    def is_doodad(self):
        return self.megagroup == 1

class Minitile:
    __slots__ = 'walkable', 'height', 'blocks_view', 'ramp', 'graphics_id', 'graphics_flipped', 'graphics'

    def __init__(self, vf4_entry, vx4_entry, minitile_graphics):
        self.walkable = bool(vf4_entry & 1)
        self.height = ((vf4_entry >> 1) & 3) / 4
        self.blocks_view = bool(vf4_entry & 8)
        self.ramp = bool(vf4_entry & 16)
        self.graphics_id = vx4_entry >> 1
        self.graphics_flipped = bool(vx4_entry & 1)

        self.graphics = minitile_graphics[self.graphics_id]
        if self.graphics_flipped:
            self.graphics = numpy.fliplr(self.graphics)

    def __hash__(self):
        return hash(self.graphics_id)

    def __eq__(self, other):
        return \
            self.walkable == other.walkable and \
            self.height == other.height and \
            self.blocks_view == other.blocks_view and \
            self.ramp == other.ramp and \
            self.graphics_id == other.graphics_id and \
            self.graphics_flipped == other.graphics_flipped

class Tileset(enum.Enum):
    """Implements an enum with all tilesets in the game

    It exposes an abstraction for reading cv5/vf4/vx4/vr4/wpe files.
    The format specs are taken from here:
    http://www.staredit.net/wiki/index.php?title=Terrain_Format
    """

    BADLANDS = 0
    SPACE_PLATFORM = 1
    INSTALLATION = 2
    ASHWORLD = 3
    JUNGLE = 4
    DESERT = 5
    ARCTIC = 6
    TWILIGHT = 7
