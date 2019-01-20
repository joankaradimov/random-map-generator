import mpq
import numpy as np
import os

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
        self.computer_players = data.count(5)
        self.human_players = data.count(6)

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        pass # TODO

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
                    print(str(e))
                finally:
                    chk_file.close()

    return scenarios
