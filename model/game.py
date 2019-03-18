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

        for dir_name, subdir_list, file_list in os.walk(directory):
            for filename in file_list:
                file_path = os.path.join(dir_name, filename)
                if filename.endswith('.chk'):
                    with open(file_path, 'rb') as chk_file:
                        scenario = self.process_chk(filename, chk_file)
                        if scenario != None:
                            scenarios.append(scenario)
                elif filename.endswith('.scm') or filename.endswith('.scx'):
                    scenario = self.process_scenario(file_path)
                    if scenario != None:
                        scenarios.append(scenario)

        return scenarios

    def process_scenario(self, scenario_path):
        filename = os.path.basename(scenario_path)
        map = mpq.MPQFile(scenario_path)
        try:
            chk_file = map.open('staredit\\scenario.chk')
            return self.process_chk(filename, chk_file)
        except Exception as e:
            pass # TODO: parse protected scenarios
        finally:
            chk_file.close()

    def process_chk(self, filename, chk_file):
        return Scenario.builder(filename, chk_file).to_scenario()
