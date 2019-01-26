import mpq
import numpy as np
import os
import struct

import config
import tileset

class ScenarioError(Exception):
    pass

class Scenario:
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

                chunk_handler = getattr(self, 'handle_' + chunk_name)
                chunk_data = chk_file.read(chunk_size)
                chunk_handler(chunk_data)
            except AttributeError:
                chk_file.seek(chunk_size, os.SEEK_CUR)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk "%s"' % chunk_name) from e
            except UnicodeDecodeError as e:
                raise ScenarioError('Invalid chunk name in file "%s"' % filename) from e

        self.__assert_attribute('human_players')
        self.__assert_attribute('tileset')
        self.__assert_attribute('height')
        self.__assert_attribute('width')

    def __assert_attribute(self, attribute):
        if not hasattr(self, attribute):
            raise ScenarioError('Required attribute "%s" missing in file "%s"' % (attribute, self.filename))

    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.is_active_player = [x == 5 or x == 6 for x in data[: 8]]
        self.computer_players = data.count(5)
        self.human_players = data.count(6)

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        data = data.ljust(20, b'\0')
        player_forces = struct.unpack('B' * 8, data[: 8])
        force_flags = struct.unpack('B' * 4, data[16: ])
        is_allied_force = [bool(x & 2) for x in force_flags]

        is_active_force = [False] * 4
        for player in range(8):
            if self.is_active_player[player]:
                is_active_force[player_forces[player]] = True

        non_allied_players = 0
        for player, force in enumerate(player_forces):
            if self.is_active_player[player] and not is_allied_force[force]:
                non_allied_players += 1

        allied_forces = 0
        for force in range(4):
            if is_active_force[force] and is_allied_force[force]:
                allied_forces += 1

        if allied_forces == 1 and non_allied_players == 0:
            self.alliances = self.is_active_player.count(True)
        else:
            self.alliances = allied_forces + non_allied_players

    def handle_ERA(self, data):
        """Handles the tileset"""
        self.tileset = tileset.Tileset(int.from_bytes(data, byteorder='little') % 8)

    def handle_DIM(self, data):
        """Handles the dimentions of the map"""
        self.width = int.from_bytes(data[:2], byteorder='little')
        self.height = int.from_bytes(data[2:], byteorder='little')

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
