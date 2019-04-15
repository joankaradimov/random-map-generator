from itertools import product
import os

import warcraft2.scenario
import warcraft2.tileset
import game
from tileset import *

class PlayerType(game.PlayerType):
    _PASSIVE_COMPUTER = 0
    _COMPUTER = 1
    PASSIVE_COMPUTER = 2
    NOBODY = 3
    COMPUTER = 4
    HUMAN = 5
    RESCUE_PASSIVE = 6
    RESCUE_ACTIVE = 7
    # 0x08 - 0xff are passive computer

class Game(game.MpqBasedGame):
    def __init__(self, game_directory):
        super().__init__(game_directory)

        self.tileset = warcraft2.tileset.Tileset
        self.player_type = PlayerType

    @classmethod
    def data_files(cls):
        return ['War2Dat.mpq']

    def process_file(self, filename, file_path):
        if filename.endswith('.pud'):
            with open(file_path, 'rb') as chk_file:
                return self.process_chk(filename, chk_file)
        else:
            return []

    def scenario_filenames(self):
        return \
            ['Campaign\\' + x % i for x, i in product(['Human\\Human%02d.pud', 'Orc\\Orc%02d.pud'], range(1, 15))] + \
            ['Campaign\\' + x % i for x, i in product(['XHuman\\2XHum%02d.pud', 'XOrc\\2XOrc%02d.pud'], range(1, 13))]

    def scenario_buider(self, filename, chk_file):
        return warcraft2.scenario.ScenarioBuilder(self, filename, chk_file)

    def tileset_basename(self, tileset):
        return {
            self.tileset.FOREST: 'Art\\bgs\\Forest\\forest',
            self.tileset.WINTER: 'Art\\bgs\\Iceland\\iceland',
            self.tileset.WASTELAND: 'Art\\bgs\\Swamp\\swamp',
            self.tileset.SWAMP: 'Art\\bgs\\XSwamp\\xswamp',
        }[tileset]

    def tiles(self, tileset):
        if tileset not in self._tiles_cache:
            cv4_entries = self.process_tileset_file(tileset, warcraft2.tileset.CV4Entry)
            dummy_vf4_entry = VF4Entry(b'0' * VF4Entry.SIZE)
            vx4_entries = self.process_tileset_file(tileset, VX4Entry)
            vr4_entries = self.process_tileset_file(tileset, VR4Entry)
            ppl_entries = self.process_tileset_file(tileset, warcraft2.tileset.PPLEntry)

            minitile_graphics = [vr4_entry.to_graphics(ppl_entries) for vr4_entry in vr4_entries]

            self._tiles_cache[tileset] = []
            for group_id, cv4_entry in enumerate(cv4_entries):
                tile_group = TileGroup(group_id, cv4_entry)
                for group_offset, megatile in enumerate(cv4_entry.megatiles):
                    vx4_entry = vx4_entries[megatile]
                    tile = Tile(tile_group, group_offset, dummy_vf4_entry, vx4_entry, minitile_graphics)
                    self._tiles_cache[tileset].append(tile)

        return self._tiles_cache[tileset]
