import itertools
import struct

class StringTable(tuple):
    def __new__(cls, tbl_file):
        data = tbl_file.read()
        string_count = struct.unpack_from('<H', data)[0]
        string_offsets = struct.unpack_from('<%dH' % string_count, data, offset=2)

        strings = []
        for offset in string_offsets:
            characters = itertools.takewhile(lambda x: x != 0, data[offset: ])
            strings.append(''.join(map(chr, characters)))

        return super(StringTable, cls).__new__(cls, strings)
