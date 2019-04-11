import struct

class CV5Entry:
    SIZE = 52
    EXTENSION = 'cv5'

    def __init__(self, data):
        self.data = struct.unpack_from('HBBHHHHHHHH', data)
        self.megatiles = struct.unpack_from('H' * 16, data, offset=20)

class WPEEntry:
    SIZE = 4
    EXTENSION = 'wpe'

    def __init__(self, data):
        self.data = numpy.array(struct.unpack_from('BBB', data), dtype=numpy.uint8)

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
