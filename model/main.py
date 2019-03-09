import os

import config
from game import *

scenarios = []
game = Game(config.STARCRAFT_ROOT)
game.process_game_scenarios()
for directory in config.MAP_DIRECTORIES:
    scenarios += game.process_scenarios(directory)
