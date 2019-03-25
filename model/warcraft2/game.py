import os
import mpq

import warcraft2.tileset
import game

class Game(game.Game):
    def __init__(self, game_directory):
        self.directory = game_directory
        self.data = mpq.MPQFile()

        self.data.add_archive(os.path.join(game_directory, 'War2Dat.mpq'))

        self.tileset = warcraft2.tileset.Tileset

    def process_mpq(self):
        return [] # TODO: implement
