import scenario

class PlayerType(scenario.PlayerType):
    _PASSIVE_COMPUTER = 0
    _COMPUTER = 1
    PASSIVE_COMPUTER = 2
    NOBODY = 3
    COMPUTER = 4
    HUMAN = 5
    RESCUE_PASSIVE = 6
    RESCUE_ACTIVE = 7
    # 0x08 - 0xff are passive computer

class ScenarioBuilder(scenario.ScenarioBuilder):
    def handle_OWNR(self, data):
        """Handles player types (e.g. human/computer/rescuable)"""
        self.player_types = list(map(PlayerType, data))

    def to_scenario(self):
        self.process_MTMX()
        # TODO: correctly parse these
        self.name = ''
        self.description = ''
        self.alliances = 1
        self.strings = []

        return Scenario(**self.__dict__)

class Scenario(scenario.Scenario):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.human_players = self.player_types.count(PlayerType.HUMAN)
        self.computer_players = self.player_types.count(PlayerType.COMPUTER)
