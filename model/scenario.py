import enum
import mpq
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
    STARCRAFT_1_00 = 59
    STARCRAFT_1_04 = 63
    STARCRAFT_EXP_BETA = 75
    STARCRAFT_EXP = 205

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

class Scenario:
    __slots__ = [
        'version', 'name', 'description', 'strings', 'filename', 'tileset', 'alliances',
        'player_types', 'human_players', 'computer_players', 'tiles', 'width', 'height'
    ]

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
                chunk_size = int.from_bytes(chk_file.read(4), byteorder='little', signed=True)

                if chunk_size < 0:
                    raise ScenarioError('Invalid chunk size for chunk "%s"' % chunk_name)

                chunk_handler_name = 'handle_' + chunk_name
                if hasattr(self, chunk_handler_name):
                    chunk_handler = getattr(self, chunk_handler_name)
                    chunk_data = chk_file.read(chunk_size)
                    chunk_handler(chunk_data)
                else:
                    chk_file.seek(chunk_size, os.SEEK_CUR)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk "%s"' % chunk_name) from e
            except UnicodeDecodeError as e:
                raise ScenarioError('Invalid chunk name in file "%s"' % filename) from e

        self.__assert_attribute('name')
        self.__assert_attribute('description')
        self.__assert_attribute('player_types')
        self.__assert_attribute('alliances')
        self.__assert_attribute('tileset')
        self.__assert_attribute('tiles')
        self.__assert_attribute('height')
        self.__assert_attribute('width')
        self.__assert_attribute('strings')

    def __assert_attribute(self, attribute):
        if not hasattr(self, attribute):
            raise ScenarioError('Required attribute "%s" missing in file "%s"' % (attribute, self.filename))

    def handle_VER(self, data):
        """Handles the version"""
        self.version = ScenarioVersion(int.from_bytes(data, byteorder='little'))

    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.player_types = list(map(PlayerType, data))
        self.computer_players = self.player_types.count(PlayerType.COMPUTER)
        self.human_players = self.player_types.count(PlayerType.HUMAN)

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        data = data.ljust(20, b'\0')
        player_forces = struct.unpack_from('B' * self.MAX_PLAYER_COUNT, data)
        force_flags = struct.unpack_from('B' * self.MAX_FORCE_COUNT, data, offset=16)
        is_active_player = [x.is_active for x in self.player_types[: self.MAX_PLAYER_COUNT]]
        is_allied_force = [bool(x & 2) for x in force_flags]

        is_active_force = [False] * self.MAX_FORCE_COUNT
        for player in range(8):
            if is_active_player[player]:
                is_active_force[player_forces[player]] = True

        non_allied_players = 0
        for player, force in enumerate(player_forces):
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

    def handle_ERA(self, data):
        """Handles the tileset"""
        tileset_index = int.from_bytes(data, byteorder='little')
        self.tileset = tileset.Tileset(tileset_index % len(tileset.Tileset))

    def handle_DIM(self, data):
        """Handles the dimentions of the map"""
        self.height, self.width = struct.unpack('<HH', data)

    def handle_MTXM(self, data):
        """Handles the map tiles"""
        tiles = [self.tileset.tiles[int.from_bytes(data[i: i + 2], byteorder='little')] for i in range(0, len(data), 2)]
        self.tiles = np.array(tiles, dtype=object).reshape(self.width, self.height)

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
        name_index, description_index = struct.unpack('<HH', data)
        if 0 < name_index < len(self.strings):
            self.name = self.strings[name_index - 1]
        else:
            self.name = self.filename

        if 0 < name_index < len(self.strings):
            self.description = self.strings[description_index - 1]
        else:
            self.description = 'Destroy all enemy buildings.'

    @property
    def graphics(self):
        return graphics.tile(self.tiles)

def process_scenarios(path):
    scenarios = []

    for dirName, subdirList, fileList in os.walk(path):
        for filename in fileList:
            if filename.endswith('.scm') or filename.endswith('.scx'):
                try:
                    map = mpq.MPQFile(os.path.join(dirName, filename))
                    chk_file = map.open('staredit\\scenario.chk')
                    scenarios.append(Scenario(filename, chk_file))
                except Exception as e:
                    pass # TODO: parse protected scenarios
                finally:
                    chk_file.close()

    return scenarios

__all__ = ['ScenarioError', 'ScenarioVersion', 'PlayerType', 'Scenario', 'process_scenarios']
