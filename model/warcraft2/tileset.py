import mpq
import numpy
import os
import struct

import tileset

class CV4Entry:
    SIZE = 42
    EXTENSION = 'cv4'

    def __init__(self, data):
        self.data = struct.unpack_from('10B', data, offset=32)
        self.megatiles = struct.unpack_from('H' * 16, data)

class PPLEntry:
    SIZE = 3
    EXTENSION = 'ppl'

    def __init__(self, data):
        self.data = numpy.array(struct.unpack_from('BBB', data), dtype=numpy.uint8)

class Tileset(tileset.BaseTileset):
    """Implements an enum with all tilesets in the game

    It exposes an abstraction for reading cv4/vx4/vr4/ppl files.
    The format specs are taken from here:
    http://cade.datamax.bg/war2x/wc2tile.html
    """

    FOREST = 0
    WINTER = 1
    WASTELAND = 2
    SWAMP = 3

    def game_archive(self):
        data = mpq.MPQFile()

        data.add_archive(r'C:\Games\Warcraft II BNE\War2Dat.mpq')

        return data

    def tileset_filename(self, entry_type):
        base_filename = {
            self.FOREST: 'Forest',
            self.WINTER: 'Iceland',
            self.WASTELAND: 'Swamp',
            self.SWAMP: 'XSwamp',
        }[self]
        return os.path.join('Art', 'bgs', base_filename, base_filename.lower() + '.' + entry_type.EXTENSION)

    @property
    def tiles(self):
        if self._tiles_cache == None:
            mpq_file = self.game_archive()
            cv4_entries = self.process(mpq_file, CV4Entry)
            dummy_vf4_entry = tileset.VF4Entry(b'0' * tileset.VF4Entry.SIZE)
            vx4_entries = self.process(mpq_file, tileset.VX4Entry)
            vr4_entries = self.process(mpq_file, tileset.VR4Entry)
            ppl_entries = self.process(mpq_file, PPLEntry)

            minitile_graphics = [vr4_entry.to_graphics(ppl_entries) for vr4_entry in vr4_entries]

            self._tiles_cache = []
            for group_id, cv4_entry in enumerate(cv4_entries):
                tile_group = tileset.TileGroup(group_id, cv4_entry)
                for group_offset, megatile in enumerate(cv4_entry.megatiles):
                    vx4_entry = vx4_entries[megatile]
                    tile = tileset.Tile(tile_group, group_offset, dummy_vf4_entry, vx4_entry, minitile_graphics)
                    self._tiles_cache.append(tile)

        return self._tiles_cache
