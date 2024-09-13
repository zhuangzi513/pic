from PIL import Image, ImageDraw, ImageFont
import BgImgConst;


class PicGen:
    def __init__(self, width, height, color, out_filename):
        self._width   =  width
        self._height  =  height
        self._bgcolor =  color
        self._bg_filename = str(self._bgcolor) + "_" + str(self._width) + "_" + str(self._height)
        self._bg_img = Image.open(self._bg_filename)
        self._bg_tile_size = BgImgConst.tile_size(self._width, self._height)

    def do_add_to_bg_img(self, target_filename, img_index_type):
        target_img = Image.open(target_filename)
        target_img.resize(self._bg_tile_size)
        target_img_position = BgImgConst.tile_position(img_index_type)
        self._bg_img.paste(target_img, target_img_position)

    def generate_final_img(self, out_filename, origin_filename, sharper_filename, color_file_name):
        do_add_to_bg_img(self, origin_filename, "origin")
        do_add_to_bg_img(self, sharper_filename, "sharper")
        do_add_to_bg_img(self, color_filename, "color")
        self._bg_img.save(out_filename)
