import mpq
import enum
import numpy as np
import os

class Tileset(enum.Enum):
    BADLANDS = 0
    SPACE_PLATFORM = 1
    INSTALLATION = 2
    ASHWORLD = 3
    JUNGLE = 4
    DESERT = 5
    ARCTIC = 6
    TWILIGHT = 7

class ScenarioError(Exception):
    pass

class ScenarioData:
    def __init__(self, chk_file):
        while chk_file.tell() != chk_file.size():
            try:
                chunk_code = chk_file.read(4)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk') from e

            try:
                chunk_name = chunk_code.decode('ascii').strip()
                chunk_size = int.from_bytes(chk_file.read(4), byteorder='little')

                chunk_handler = getattr(self, 'handle_' + chunk_name)
                chunk_data = chk_file.read(chunk_size)
                chunk_handler(chunk_data)
            except AttributeError:
                chk_file.seek(chunk_size, os.SEEK_CUR)
            except mpq.storm.error as e:
                raise ScenarioError('Error reading chunk "%s"' % chunk_name) from e
            except UnicodeDecodeError as e:
                raise ScenarioError('Invalid chunk name') from e

    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.computer_players = data.count(5)
        self.human_players = data.count(6)

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        pass # TODO

    def handle_ERA(self, data):
        """Handles the tileset"""
        self.tileset = Tileset(int.from_bytes(data, byteorder='little') % 8)

    def handle_DIM(self, data):
        """Handles the dimentions of the map"""
        self.width = int.from_bytes(data[:2], byteorder='little')
        self.height = int.from_bytes(data[2:], byteorder='little')

    def handle_MTXM(self, data):
        """Handles the map tiles"""
        tiles = [int.from_bytes(data[i: i + 2], byteorder='little') for i in range(0, len(data), 2)]
        self.tiles = np.array(tiles).reshape(self.width, self.height)

    def xhandle_UNIT(self, data):
        """Handles the units on the map"""
        pass # TODO: extract start location and resources data

    def xhandle_THG2(self, data):
        """Handles the thingies on the map"""
        pass # TODO: extract trees and other decorations

scenario_data = []
for dirName, subdirList, fileList in os.walk('C:/Games/StarCraft/Maps'):
    for filename in fileList:
        try:
            map = mpq.MPQFile(os.path.join(dirName, filename))
            chk_file = map.open('staredit\\scenario.chk')
            x = ScenarioData(chk_file)
            # print(filename, ' - ', x.tileset, ' (', x.width, ' X ', x.height, ')')
            if x.tileset == Tileset.JUNGLE and x.width == 128 and x.height == 128:
                scenario_data.append(x)
        except Exception as e:
            print(str(e) + '; Skipping scenario:', filename)
        finally:
            chk_file.close()

print('DONE.')
print('Total scenarios:', len(scenario_data))
