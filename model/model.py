import mpq
import numpy as np
import os

import config
from scenario import *
from tileset import Tileset

print('Jungle tiles:', len(Tileset.JUNGLE.tiles))

scenarios = []
scenarios += process_scenarios(os.path.join(config.STARCRAFT_ROOT, 'Maps'))
for directory in config.MAP_DIRECTORIES:
    scenarios += process_scenarios(directory)

four_player_jungle_scenarios = [x for x in scenarios if x.human_players == 4 and x.tileset == Tileset.JUNGLE and x.width == 128 and x.height == 128]

print('DONE.')
print('Total scenarios:', len(scenarios))
print('Four player jungle scenarios:', len(four_player_jungle_scenarios))
