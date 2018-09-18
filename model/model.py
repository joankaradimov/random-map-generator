import mpq
import numpy
import os

class ScenarioData:
    def __init__(self, chk_file):
        while chk_file.tell() != chk_file.size():
            chunk_name = chk_file.read(4).decode('ascii').strip()
            chunk_size = int.from_bytes(chk_file.read(4), byteorder='little')

            try:
                chunk_handler = getattr(self, 'handle_' + chunk_name)
                chunk_data = chk_file.read(chunk_size)
                chunk_handler(chunk_data)
            except AttributeError:
                chk_file.seek(chunk_size, os.SEEK_CUR)

    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.computer_players = data.count(5)
        self.human_players = data.count(6)

    def handle_FORC(self, data):
        """Handles force (alliance) information"""
        pass # TODO

    def handle_ERA(self, data):
        """Handles the tileset"""
        self.tileset = int.from_bytes(data, byteorder='little')

    def handle_DIM(self, data):
        """Handles the dimentions of the map"""
        self.width = int.from_bytes(data[:2], byteorder='little')
        self.height = int.from_bytes(data[2:], byteorder='little')

    def handle_MTXM(self, data):
        """Handles the map tiles"""
        tiles = [int.from_bytes(data[i: i + 2], byteorder='little') for i in range(0, len(data), 2)]
        self.tiles = numpy.array(tiles).reshape(self.width, self.height)

    def handle_UNIT(self, data):
        """Handles the units on the map"""
        pass # TODO: extract start location and resources data

    def handle_THG2(self, data):
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
            if x.tileset == 4 and x.width == 128 and x.height == 128:
                scenario_data.append(x)
        except Exception as e:
            print(str(e) + '; Skipping scenario:', filename)
        finally:
            chk_file.close()

print('DONE.')
print('Total scenarios:', len(scenario_data))
