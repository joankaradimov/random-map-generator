import enum
import numpy
import struct

import tileset

class CV4Entry:
    SIZE = 42
    EXTENSION = 'cv4'

    def __init__(self, data):
        self.data = struct.unpack_from('10B', data, offset=32)
        self.megatiles = struct.unpack_from('H' * 16, data)

class PPLEntry:
    SIZE = 3
    EXTENSION = 'ppl'

    def __init__(self, data):
        self.data = numpy.array(struct.unpack_from('BBB', data), dtype=numpy.uint8)

class Tileset(enum.Enum):
    """Implements an enum with all tilesets in the game

    It exposes an abstraction for reading cv4/vx4/vr4/ppl files.
    The format specs are taken from here:
    http://cade.datamax.bg/war2x/wc2tile.html
    """

    FOREST = 0
    WINTER = 1
    WASTELAND = 2
    SWAMP = 3
