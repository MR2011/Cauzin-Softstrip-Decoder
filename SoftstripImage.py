import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image
import numpy as np
import imutils
import copy
from imutils import perspective


INCREASE = 1
DECREASE = -1
UP = -1
DOWN = 1
IMG_RESIZE = 50
PEN_SIZE = 10
MINIATURE_WIDTH = 400
DEGREE = 90


class SoftstripImage:

    def __init__(self, path, cv2_img=None):
        if path:
            self.path = path
            self.original_cv2_img = cv2.imread(path) 
        elif cv2_img.size > 0 :
            self.original_cv2_img = cv2_img
        rows, self.original_width, channels = self.original_cv2_img.shape
        self.resize_width = self.original_width
        self.cv2_img = copy.deepcopy(self.original_cv2_img)
        self._update_images()

    def perspective_transformation(self, transformation_points):
        pts = np.array(transformation_points)
        self.cv2_img = perspective.four_point_transform(self.cv2_img, pts)
        self._update_images()

    def resize(self, change_width):
        self.resize_width += change_width
        if self.resize_width < self.original_width:
            interpolation = cv2.INTER_AREA
        elif self.resize_width > self.original_width:
            interpolation = cv2.INTER_CUBIC
        else:
            self.cv2_img = copy.deepcopy(self.original_cv2_img)
            return
        self.cv2_img = imutils.resize(self.original_cv2_img, width=self.resize_width, inter=interpolation)
        self._update_images()

    def _update_images(self):
        self.qimg = self.convert_opencv_to_qimg(self.cv2_img)
        self.pixmap = QPixmap.fromImage(self.qimg)

    def rotate(self, angle):
        self.cv2_img = imutils.rotate_bound(self.cv2_img, angle=angle)
        self._update_images()

    def autocrop(self):
        gray_img = cv2.cvtColor(self.cv2_img, cv2.COLOR_BGR2GRAY)
        self.gray_img = gray_img
        blur = cv2.GaussianBlur(gray_img, (5,5), 0)
        ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _, self.binary_img = cv2.threshold(self.cv2_img, 127, 255, cv2.THRESH_BINARY)
        thresh_not = cv2.bitwise_not(thresh)
        src, contours, hierarchy = cv2.findContours(thresh_not, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        while len(contours) > 1:
            thresh_not = cv2.GaussianBlur(thresh_not, (3,3), 0)
            src, contours, hierarchy = cv2.findContours(thresh_not, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hull = cv2.convexHull(contours[0])

        cv2.drawContours(self.cv2_img, [hull], -1, (255, 0, 0), 1)
        self._update_images()

    @staticmethod
    def convert_opencv_to_qimg(cv_img):
        qformat = QImage.Format_Indexed8
        if len(cv_img.shape) == 3:
            if cv_img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        qimg = QImage(cv_img, cv_img.shape[1], cv_img.shape[0], cv_img.strides[0], qformat)
        qimg = qimg.rgbSwapped()
        return qimg