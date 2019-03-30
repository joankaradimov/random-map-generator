import enum
import numpy as np
import os
import struct

import graphics

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
    @property
    def is_active(self):
        return self == self.HUMAN or self == self.COMPUTER

class ScenarioBuilder:
    MAX_PLAYER_COUNT = 8
    MAX_FORCE_COUNT = 4

    def __init__(self, game, filename, chk_file):
        self.game = game
        self.filename = filename
        while True:
            try:
                chunk_code = chk_file.read(4)
                if len(chunk_code) < 4:
                    break
            except Exception as e:
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
            except Exception as e:
                raise ScenarioError('Error reading chunk "%s"' % chunk_name) from e

    def handle_VER(self, data):
        """Handles the version"""
        self.version = ScenarioVersion(int.from_bytes(data, byteorder='little'))

    def handle_ERA(self, data):
        """Handles the tileset"""
        tileset_index = int.from_bytes(data, byteorder='little')
        self.tileset = self.game.tileset(tileset_index % len(self.game.tileset))

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

    def get_tile(self, tile_index):
        return self.tileset.tiles[tile_index if tile_index < len(self.tileset.tiles) else 0]

class Scenario:
    __slots__ = [
        'version', 'name', 'description', 'strings', 'filename', 'tileset', 'alliances',
        'player_types', 'human_players', 'computer_players', 'tiles', 'game',
    ]

    def __init__(self, game, name, description, version, strings, tileset, filename, alliances, player_types, tiles):
        self.game = game
        self.name = name
        self.description = description
        self.version = version
        self.filename = filename
        self.strings = strings
        self.tileset = tileset
        self.alliances = alliances
        self.player_types = player_types
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
    def builder(game, filename, chk_file):
        return ScenarioBuilder(game, filename, chk_file)

__all__ = ['ScenarioError', 'ScenarioVersion', 'PlayerType', 'Scenario']
