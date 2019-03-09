import mpq
import os

from scenario import *

class Game:
    def __init__(self, game_directory):
        self.directory = game_directory

    def process_game_scenarios(self):
        maps_directory = os.path.join(self.directory, 'Maps')
        return self.process_scenarios(maps_directory)

    def process_scenarios(self, directory):
        scenarios = []

        for dirName, subdirList, fileList in os.walk(directory):
            for filename in fileList:
                if filename.endswith('.scm') or filename.endswith('.scx'):
                    try:
                        map = mpq.MPQFile(os.path.join(dirName, filename))
                        chk_file = map.open('staredit\\scenario.chk')
                        scenario = ScenarioBuilder(filename, chk_file).to_scenario()
                        scenarios.append(scenario)
                    except Exception as e:
                        pass # TODO: parse protected scenarios
                    finally:
                        chk_file.close()

        return scenarios
