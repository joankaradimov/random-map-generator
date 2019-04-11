import mpq
import os

from tileset import *
import starcraft.scenario
import starcraft.tileset
from string_table import *
import game

class PlayerType(game.PlayerType):
    INACTIVE = 0
    RESCUE_PASSIVE = 3
    UNUSED = 4
    COMPUTER = 5
    HUMAN = 6
    NEUTRAL = 7

class Game(game.Game):
    def __init__(self, game_directory):
        super().__init__(game_directory)

        self.tileset = Tileset
        self.player_type = PlayerType

    @classmethod
    def data_files(cls):
        return [
            'Starcraft.mpq',
            'Broodwar.mpq',
            'StarDat.mpq',
            'BrooDat.mpq',
            'patch_rt.mpq',
            'patch_ed.mpq',
        ]

    def process_file(self, filename, file_path):
        if filename.endswith('.chk'):
            with open(file_path, 'rb') as chk_file:
                return self.process_chk(filename, chk_file)
        elif filename.endswith('.scm') or filename.endswith('.scx'):
            map = mpq.MPQFile(file_path)
            try:
                chk_file = map.open('staredit\\scenario.chk')
                return self.process_chk(filename, chk_file)
            finally:
                chk_file.close()
        else:
            return []

    def scenario_filenames(self):
        map_data = self.data.open('arr\mapdata.tbl')
        try:
            return [x + '\\staredit\\scenario.chk' for x in StringTable(map_data)]
        except mpq.storm.error as e:
            return []
        finally:
            map_data.close()

    def scenario_buider(self, filename, chk_file):
        return starcraft.scenario.ScenarioBuilder(self, filename, chk_file)

    def tileset_basename(self, tileset):
        return {
            self.tileset.BADLANDS: 'tileset\\badlands',
            self.tileset.SPACE_PLATFORM: 'tileset\\platform',
            self.tileset.INSTALLATION: 'tileset\\install',
            self.tileset.ASHWORLD: 'tileset\\ashworld',
            self.tileset.JUNGLE: 'tileset\\jungle',
            self.tileset.DESERT: 'tileset\\Desert',
            self.tileset.ARCTIC: 'tileset\\Ice',
            self.tileset.TWILIGHT: 'tileset\\Twilight',
        }[tileset]

    def tiles(self, tileset):
        if tileset not in self._tiles_cache:
            cv5_entries = self.process_tileset_file(tileset, starcraft.tileset.CV5Entry)
            vf4_entries = self.process_tileset_file(tileset, VF4Entry)
            vx4_entries = self.process_tileset_file(tileset, VX4Entry)
            vr4_entries = self.process_tileset_file(tileset, VR4Entry)
            wpe_entries = self.process_tileset_file(tileset, starcraft.tileset.WPEEntry)

            minitile_graphics = [vr4_entry.to_graphics(wpe_entries) for vr4_entry in vr4_entries]

            self._tiles_cache[tileset] = []
            for group_id, cv5_entry in enumerate(cv5_entries):
                tile_group = TileGroup(group_id, cv5_entry)
                for group_offset, megatile in enumerate(cv5_entry.megatiles):
                    vf4_entry = vf4_entries[megatile]
                    vx4_entry = vx4_entries[megatile]
                    tile = Tile(tile_group, group_offset, vf4_entry, vx4_entry, minitile_graphics)
                    self._tiles_cache[tileset].append(tile)

        return self._tiles_cache[tileset]
