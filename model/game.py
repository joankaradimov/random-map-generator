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
                if filename.endswith('.chk'):
                    chk_path = os.path.join(dirName, filename)
                    with open(chk_path, 'rb') as chk_file:
                        scenario = self.process_chk(filename, chk_file)
                        if scenario != None:
                            scenarios.append(scenario)
                if filename.endswith('.scm') or filename.endswith('.scx'):
                    scenario = self.process_scenario(os.path.join(dirName, filename))
                    if scenario != None:
                        scenarios.append(scenario)

        return scenarios

    def process_scenario(self, scenario_path):
        try:
            map = mpq.MPQFile(scenario_path)
            chk_file = map.open('staredit\\scenario.chk')
            filename = os.path.basename(scenario_path)
            return self.process_chk(filename, chk_file)
        except Exception as e:
            pass # TODO: parse protected scenarios
        finally:
            chk_file.close()

    def process_chk(self, filename, chk_file):
        return ScenarioBuilder(filename, chk_file).to_scenario()
