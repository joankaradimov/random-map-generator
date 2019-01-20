import matplotlib.pyplot as plt
import mpq
import numpy as np
import os

import config
from scenario import *
from tileset import Tileset

scenarios = []
scenarios += process_scenarios(os.path.join(config.STARCRAFT_ROOT, 'Maps'))
for directory in config.MAP_DIRECTORIES:
    scenarios += process_scenarios(directory)

four_player_jungle_scenarios = [x for x in scenarios if x.human_players == 4 and x.tileset == Tileset.JUNGLE and x.width == 128 and x.height == 128]

def tile_average_height(tile):

    @np.vectorize
    def minitile_heights(minitile):
        return minitile.height

    return np.average(minitile_heights(tile.minitiles))

scenario = four_player_jungle_scenarios[13]
tile_heights = np.vectorize(tile_average_height)(scenario.tiles)

plt.figure()
plt.suptitle(scenario.filename)
plt.imshow(tile_heights, cmap=plt.cm.Blues)
plt.show()
