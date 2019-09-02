# TODO: implement this using the specs from here:
# http://atariage.com/forums/topic/154725-warcraft-map-data/

class Game(game.MpqBasedGame):
    @classmethod
    def data_files(cls):
        return ['data/data.war']
