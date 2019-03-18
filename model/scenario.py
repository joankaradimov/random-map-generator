import enum
import numpy as np
import os
import struct

import config
import graphics
import tileset

class ScenarioError(Exception):
    pass

class ScenarioVersion(enum.Enum):
    WARCRAFT2 = 17
    WARCRAFT2_EXP = 19
    STARCRAFT_BETA = 47
    STARCRAFT_VANILLA = 59
    STARCRAFT_1_04 = 63
    STARCRAFT_REMASTERED = 64
    BROOD_WAR_BETA = 75
    BROOD_WAR = 205
    BROOD_WAR_REMASTERED = 206

class PlayerType(enum.Enum):
    INACTIVE = 0
    RESCUE_PASSIVE = 3
    UNUSED = 4
    COMPUTER = 5
    HUMAN = 6
    NEUTRAL = 7

    @property
    def is_active(self):
        return self == self.HUMAN or self == self.COMPUTER

class ScenarioBuilder:
    MAX_PLAYER_COUNT = 8
    MAX_FORCE_COUNT = 4

    def __init__(self, filename, chk_file):
        self.filename = filename
        while chk_file.tell() != chk_file.size():
            try:
                chunk_code = chk_file.read(4)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk in file "%s"' % filename) from e

            try:
                chunk_name = chunk_code.decode('ascii').strip()
            except UnicodeDecodeError as e:
                chunk_name = ''

            try:
                chunk_size = int.from_bytes(chk_file.read(4), byteorder='little', signed=True)
                chunk_handler_name = 'handle_' + chunk_name
                if chunk_size > 0 and hasattr(self, chunk_handler_name):
                    chunk_handler = getattr(self, chunk_handler_name)
                    chunk_data = chk_file.read(chunk_size)
                    chunk_handler(chunk_data)
                else:
                    chk_file.seek(chunk_size, os.SEEK_CUR)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk "%s"' % chunk_name) from e

    def handle_VER(self, data):
        """Handles the version"""
        self.version = ScenarioVersion(int.from_bytes(data, byteorder='little'))

    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.player_types = list(map(PlayerType, data))

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        data = data.ljust(20, b'\0')
        self.player_forces = struct.unpack_from('B' * self.MAX_PLAYER_COUNT, data)
        self.force_flags = struct.unpack_from('B' * self.MAX_FORCE_COUNT, data, offset=16)

    def process_FORC(self):
        is_active_player = [x.is_active for x in self.player_types[: self.MAX_PLAYER_COUNT]]
        is_allied_force = [bool(x & 2) for x in self.force_flags]

        is_active_force = [False] * self.MAX_FORCE_COUNT
        for player in range(8):
            if is_active_player[player]:
                is_active_force[self.player_forces[player]] = True

        non_allied_players = 0
        for player, force in enumerate(self.player_forces):
            if is_active_player[player] and not is_allied_force[force]:
                non_allied_players += 1

        allied_forces = 0
        for force in range(self.MAX_FORCE_COUNT):
            if is_active_force[force] and is_allied_force[force]:
                allied_forces += 1

        if allied_forces == 1 and non_allied_players == 0:
            self.alliances = is_active_player.count(True)
        else:
            self.alliances = allied_forces + non_allied_players

        del self.player_forces
        del self.force_flags

    def handle_ERA(self, data):
        """Handles the tileset"""
        tileset_index = int.from_bytes(data, byteorder='little')
        self.tileset = tileset.Tileset(tileset_index % len(tileset.Tileset))

    def handle_DIM(self, data):
        """Handles the dimentions of the map"""
        self.height, self.width = struct.unpack('<HH', data)

    def handle_MTXM(self, data):
        """Handles the map tiles"""
        if hasattr(self, 'mtmx_data'):
            self.mtmx_data += data
        else:
            self.mtmx_data = data

    def process_MTMX(self):
        tiles = struct.unpack_from('<%dH' % (self.width * self.height), self.mtmx_data)
        tiles = [self.get_tile(tile) for tile in tiles]
        self.tiles = np.array(tiles, dtype=object).reshape(self.width, self.height)
        del self.width
        del self.height
        del self.mtmx_data

    def xhandle_UNIT(self, data):
        """Handles the units on the map"""
        pass # TODO: extract start location and resources data

    def xhandle_THG2(self, data):
        """Handles the thingies on the map"""
        pass # TODO: extract trees and other decorations

    def handle_STR(self, data):
        string_count = int.from_bytes(data[:2], byteorder='little')
        offsets = struct.unpack_from('<%dH' % string_count, data, offset=2)

        self.strings = []
        for i in range(string_count):
            string_start = offsets[i]
            string_end = data.find(b'\0', string_start)
            self.strings.append(data[string_start: string_end].decode('ISO-8859-1'))

    def handle_SPRP(self, data):
        self.name_index, self.description_index = struct.unpack('<HH', data)

    def process_SPRP(self):
        if hasattr(self, 'name_index') and 0 < self.name_index < len(self.strings):
            self.name = self.strings[self.name_index - 1]
        else:
            self.name = self.filename

        if hasattr(self, 'description_index') and 0 < self.description_index < len(self.strings):
            self.description = self.strings[self.description_index - 1]
        else:
            self.description = 'Destroy all enemy buildings.'

        del self.name_index
        del self.description_index

    def get_tile(self, tile_index):
        return self.tileset.tiles[tile_index if tile_index < len(self.tileset.tiles) else 0]

    def to_scenario(self):
        self.process_FORC()
        self.process_MTMX()
        self.process_SPRP()

        return Scenario(**self.__dict__)

class Scenario:
    """Implements a StarCraft scenario.

    The format specs are taken from here:
    http://www.staredit.net/wiki/index.php?title=Scenario.chk
    """

    __slots__ = [
        'version', 'name', 'description', 'strings', 'filename', 'tileset', 'alliances',
        'player_types', 'human_players', 'computer_players', 'tiles'
    ]

    def __init__(self, name, description, version, strings, tileset, filename, alliances, player_types, tiles):
        self.name = name
        self.description = description
        self.version = version
        self.filename = filename
        self.strings = strings
        self.tileset = tileset
        self.alliances = alliances
        self.player_types = player_types
        self.human_players = player_types.count(PlayerType.HUMAN)
        self.computer_players = player_types.count(PlayerType.COMPUTER)
        self.tiles = tiles

        self.__assert_attribute('name')
        self.__assert_attribute('description')
        self.__assert_attribute('player_types')
        self.__assert_attribute('alliances')
        self.__assert_attribute('tileset')
        self.__assert_attribute('tiles')

    def __assert_attribute(self, attribute):
        if not hasattr(self, attribute):
            raise ScenarioError('Required attribute "%s" missing in file "%s"' % (attribute, self.filename))

    @property
    def width(self):
        return self.tiles.shape[0]

    @property
    def height(self):
        return self.tiles.shape[1]

    @property
    def graphics(self):
        return graphics.tile(self.tiles)

    @staticmethod
    def builder(filename, chk_file):
        return ScenarioBuilder(filename, chk_file)

    def to_chunk_data(self):
        result = b''

        result += b'TYPE'
        result += struct.pack('<L', 4)
        result += b'RAWB'

        result += b'VER '
        result += struct.pack('<L', 2)
        result += struct.pack('<H', ScenarioVersion.STARCRAFT_EXP.value)

        # TODO: VCOD

        result += b'OWNR'
        result += struct.pack('<L', 12)
        for i in range(8):
            player_type = PlayerType.HUMAN if i < self.human_players else PlayerType.INACTIVE
            result += struct.pack('B', player_type.value)

        for i in range(4):
            result += struct.pack('B', PlayerType.INACTIVE.value)

        result += b'ERA '
        result += struct.pack('<L', 2)
        result += struct.pack('<H', self.tileset.value)

        result += b'DIM '
        result += struct.pack('<L', 4)
        result += struct.pack('<HH', self.width, self.height)

        result += b'SIDE'
        result += struct.pack('<L', 12)
        # 4 for "neutral", 5 for "user selectable", 7 for "inactive"
        for i in range(8):
            side = 5 if i < self.human_players else 7
            result += struct.pack('B', side)
        result += struct.pack('BBBB', 7, 7, 7, 4)

        result += b'MTMX'
        result += struct.pack('<L', self.width * self.height * 2)
        for y in range(self.height):
            for x in range(self.width):
                result += struct.pack('<H', self.tiles[y, x].index)

        result += b'UNIT' # TODO: unit data
        result += struct.pack('<L', 0)

        result += b'THG2' # TODO: thingies data
        result += struct.pack('<L', 0)

        result += b'STR ' # TODO: strings
        result += struct.pack('<L', 2)
        result += struct.pack('<H', 0)

        result += b'SPRP' # TODO: name and description
        result += struct.pack('<L', 4)
        result += struct.pack('<HH', 0, 0)

        result += b'FORC' # TODO: make this human readable
        result += struct.pack('<L', 20)
        result += b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\1\1\1\1'

        result += b'COLR' # TODO: make this human readable
        result += struct.pack('<L', 8)
        result += b'\0\1\2\3\4\5\6\7'

        return result

__all__ = ['ScenarioError', 'ScenarioVersion', 'PlayerType', 'Scenario']
