import numpy

def tile(tiles):
    array_width, array_height = tiles.shape
    tile_graphics = tiles[0, 0].graphics
    tile_width, tile_height, *remaining = tile_graphics.shape
    result_width = array_width * tile_width
    result_height = array_height * tile_height

    result = numpy.zeros([result_width, result_height, *remaining], dtype=tile_graphics.dtype)

    for x in range(0, result_width, tile_width):
        for y in range(0, result_height, tile_height):
            result[x:x+tile_width, y:y+tile_height] = tiles[x // tile_width, y // tile_height].graphics

    return result
