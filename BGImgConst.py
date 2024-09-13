class BgImgConst:
    def __init__(self, bg_width, bg_height):
        self._width = bg_width
        self._height = bg_height

    def compute_position(self, tile_index):
        return (0,1)

    def tile_size(self, bg_width, bg_height):
        return (10, 10)

    def tile_position(self, bg_width, bg_height, tile_index_type):
        tile_index_ = -1
        if (tile_index_type == "origin"):
            tile_index = 0
        elif (tile_index_type == ""):
            tile_index = 1
        elif (tile_index_type == ):
            tile_index = 2

        pos_x, pos_y = compute_position(self, tile_index)
        return (pos_x, pos_y)
