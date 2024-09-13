import numpy as np
import cv2 as cv

class CategoryClassfy:
    def __init__(self, src_filename, target_filename):
        self.src_file_name = src_filename
        self.target_file_name = target_filename
        #self.origin_img = cv.imread(filename, cv2.IMREAD_COLOR)
        self.origin_img = cv.imread(filename, cv2.IMREAD_GRAYSCALE)
        self._height = origin_img.shape[0]
        self._width = origin_img.shape[1]
        self._channels = origin_img.shape[2]

    def laplacian(self):
        laplacian_img = cv.Laplacian(src=origin_img, ddepth=cv.CV_64F, ksize=3)
        self.sharpe_img = cv2.convertScaleAbs(laplacian_img)

    def sobel(self):
        sobel_img = cv.Sobel(src=origin_img, ddepth=cv.CV_64F, dx=1, dy=1, ksize=3)
        self.sharpe_img = cv2.convertScaleAbs(sobel_img)

    def classfy(self):
        count_none_zeros = 0

        #_R,_G,_B = cv2.split(self.sharpe_img)
        for y in range(0, self._height):
            for x in range(0, self._width):
                if self.sharpe_img[y, x] > 0:
                    count_none_zeros += 1

        return count_none_zeros/(self._height*self._width)

    def save(self):
        cv.imgwrite(self.target_file_name, self.sharpe_img)
