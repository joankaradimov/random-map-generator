import mpq
import os

from scenario import *
from string_table import *

class Game:
    def __init__(self, game_directory):
        self.directory = game_directory

    def process_game_scenarios(self):
        scenarios = []
        data = mpq.MPQFile()
        try:
            data.add_archive(os.path.join(self.directory, 'Starcraft.mpq'))
            data.add_archive(os.path.join(self.directory, 'Broodwar.mpq'))
            data.add_archive(os.path.join(self.directory, 'StarDat.mpq'))
            data.add_archive(os.path.join(self.directory, 'BrooDat.mpq'))
            data.add_archive(os.path.join(self.directory, 'patch_rt.mpq'))
            data.add_archive(os.path.join(self.directory, 'patch_ed.mpq'))
            scenarios += self.process_mpq(data)
        finally:
            data.close()

        scenarios += self.process_scenarios(os.path.join(self.directory, 'Maps'))
        return scenarios

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

    def process_mpq(self, data):
        scenarios = []
        map_data = data.open('arr\mapdata.tbl')
        try:
            chk_files = StringTable(map_data)
        except mpq.storm.error as e:
            return scenarios
        finally:
            map_data.close()

        for filename in chk_files:
            chk_file = None
            try:
                chk_file = data.open(filename + '\\staredit\\scenario.chk')
                scenario = self.process_chk(os.path.basename(filename), chk_file)
                scenarios.append(scenario)
            except Exception as e:
                pass
            finally:
                if chk_file != None:
                    chk_file.close()

        return scenarios
