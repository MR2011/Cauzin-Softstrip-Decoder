import cv2
from collections import Counter

class SoftstripMatrix:
    """
        Represents the Softstrip with a 2D array.
    """
    def __init__(self, img, grayscale_img):
        self.create_matrices(img, grayscale_img)

    def create_matrices(self, img, grayscale_img):
        """
            Creates the following 2D matrices:
            - binary
            - grayscale
        """
        # The dilated img has less noise in the start bar
        # so the binary matrix uses the start bar from the
        # dilated img instead of the original img
        dilated_img = self.create_dilated_img(img)
        rows, columns, _ = img.shape
        self.binary_matrix = []
        self.grayscale_matrix = []
        current_img = img
        last_black_pixel_position = 0

        for row in range(rows):
            current_img = dilated_img
            binary_row = []
            grayscale_row = []
            for column in range(columns):
                pixel = current_img[row, column]
                if pixel[0] == 0:
                    binary_row.append(1) # I know...a black pixel is supposed to be a 0
                    grayscale_row.append(grayscale_img[row, column])
                    if (len(binary_row) - 1) > last_black_pixel_position:
                        last_black_pixel_position = len(binary_row) - 1
                elif pixel[0] == 255:
                    if len(binary_row) > 0: # Don't append pixels from the quiet zone
                        current_img = img
                        binary_row.append(0) # ... and white pixels are supposed to be 1s
                        grayscale_row.append(grayscale_img[row, column])
            self.binary_matrix.append(binary_row)
            self.grayscale_matrix.append(grayscale_row)
        self.normalize_matrices(last_black_pixel_position)

    def create_dilated_img(self, img):
        """
            Applies dilation with a 5x5 kernel and 3 iterations
        """
        copy = img.copy()
        _, threshold = cv2.threshold(copy, 127, 255, cv2.THRESH_BINARY)
        inverted = cv2.bitwise_not(threshold)
        inverted_dilated = cv2.dilate(inverted, (5,5), iterations=3)
        dilated = cv2.bitwise_not(inverted_dilated)
        return dilated
    
    def normalize_matrices(self, last_black_pixel_position):
        """
            Normalizes all rows so that they have all the same size
        """
        # Remove all pixels after the last black pixel position
        # If a row is too small, repeat the last pixel
        avg_row_len = 0
        for index, row in enumerate(self.binary_matrix):
            if len(row) > 0:
                del self.binary_matrix[index][(last_black_pixel_position + 1):]
                del self.grayscale_matrix[index][(last_black_pixel_position + 1):]
                while len(self.binary_matrix[index]) < (last_black_pixel_position + 1):
                    self.binary_matrix[index].append(self.binary_matrix[index][-1])
                    self.grayscale_matrix[index].append(self.grayscale_matrix[index][-1])
                avg_row_len += len(self.binary_matrix[index])
        avg_row_len /= len(self.binary_matrix)
        # Remove all rows < average row length
        remove = list()
        for index, row in enumerate(self.binary_matrix):
            if len(row) < avg_row_len:
                remove.append(index)
        for i in reversed(remove):
            del self.binary_matrix[i]
            del self.grayscale_matrix[i]

    def print_pixel_matrix(self):
        for row in self.pixel_matrix:
            row_string = ''.join(map(str, row))
            print(row_string)
    
    def print_gray_pixel_matrix(self):
        for row in self.gray_matrix:
            print(row)