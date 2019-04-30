import os

import config
from game import Game

if __name__ == '__main__':
    scenarios = []
    game = Game.create(config.STARCRAFT_ROOT)
    scenarios += game.process_game_scenarios()
    for directory in config.MAP_DIRECTORIES:
        scenarios += game.process_directory(directory)

    print(len(scenarios))
