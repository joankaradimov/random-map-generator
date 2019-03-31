import scenario

class ScenarioBuilder(scenario.ScenarioBuilder):
    def to_scenario(self):
        self.process_MTMX()
        # TODO: correctly parse these
        self.name = ''
        self.description = ''
        self.alliances = 1
        self.strings = []

        return Scenario(**self.__dict__)

class Scenario(scenario.Scenario):
    pass
