import scenario

class ScenarioBuilder(scenario.ScenarioBuilder):
    def handle_DESC(self, data):
        self.description = data.decode('ISO-8859-1').strip('\0')

    def to_scenario(self):
        self.process_MTMX()
        # TODO: correctly parse these
        self.name = ''
        self.alliances = 1
        self.strings = []

        return Scenario(**self.__dict__)

class Scenario(scenario.Scenario):
    """Implements a Warcraft 2 scenario.

    The format specs are taken from here:
    http://cade.datamax.bg/war2x/pudspec.html
    """
    pass
