import mpq
import enum
import os

import config

class Tileset(enum.Enum):
    BADLANDS = 0
    SPACE_PLATFORM = 1
    INSTALLATION = 2
    ASHWORLD = 3
    JUNGLE = 4
    DESERT = 5
    ARCTIC = 6
    TWILIGHT = 7

    @property
    def mpq_filename(self):
        if self.value < 5:
            return 'StarDat.mpq'
        else:
            return 'BroodDat.mpq'

    @property
    def tileset_filename(self):
        return {
            self.BADLANDS: 'badlands',
            self.SPACE_PLATFORM: 'platform',
            self.INSTALLATION: 'install',
            self.ASHWORLD: 'ashworld',
            self.JUNGLE: 'jungle',
            self.DESERT: 'Desert',
            self.ARCTIC: 'Ice',
            self.TWILIGHT: 'Twilight',
        }[self]

    def load_data(self):
        self.cv5_entries = self.process('cv5', 52)
        self.vf4_entries = self.process('vf4', 32)
        self.vx4_entries = self.process('vx4', 32)

    def process(self, extension, size):
        mpq_file = mpq.MPQFile(os.path.join(config.STARCRAFT_ROOT, self.mpq_filename))
        try:
            file = mpq_file.open(os.path.join('tileset', self.tileset_filename + '.' + extension))

            entries = []
            while file.tell() != file.size():
                entries.append(file.read(size))

            return entries
        finally:
            file.close()

