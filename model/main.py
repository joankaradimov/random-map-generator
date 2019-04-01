import os

import config

import starcraft.game
import warcraft2.game

def create_game(game_directory):
    games_types = [warcraft2.game.Game, starcraft.game.Game]
    for game in games_types:
        data_file_paths = (os.path.join(game_directory, x) for x in game.data_files())
        if all(os.path.exists(x) for x in data_file_paths):
            return game(game_directory)

scenarios = []
game = Game(config.STARCRAFT_ROOT)
scenarios += game.process_game_scenarios()
for directory in config.MAP_DIRECTORIES:
    scenarios += game.process_scenarios(directory)
