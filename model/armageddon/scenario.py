import scenario

class ScenarioBuilder:
    def __init__(self, filename, file):
        pass

    def to_scenario(self):
        return Scenario(**self.__dict__)

class Scenario(scenario.Scenario):
    pass
