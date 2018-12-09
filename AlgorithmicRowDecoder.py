from collections import Counter
import numpy as np
import cv2
import datetime
import copy
from Utils import *


class AlgorithmicRowDecoder:
    """
        Algorithmic approach to decode the dibits in a row.
        First, the sizes of all color areas are determined.
        Next, it is determined which areas are one unit and which
        are two units wide (2 units = 1 dibit). Lastly, it is checked
        if a three wide unit is included before the rack starts.
    """

    def __init__(self, grouped_matrix, bits_count, start_time, timeout):
        self.grouped_matrix = grouped_matrix
        self.bits_count = bits_count
        self.start_time = start_time
        self.timeout = timeout

    def decode_rows(self):
        return self.reduce_grouped_matrix(self.grouped_matrix)

    def reduce_grouped_matrix(self, matrix):
        """
            At this point, a row consists of multiple pixel lines.
            They are reduced to a single pixel lines (decoded)
        """
        new_pixel_matrix = []
        for index, row in enumerate(matrix):
            if len(row) > 0:
                now = datetime.datetime.now().replace(microsecond=0)
                difference = now - self.start_time
                if (difference.seconds // 60) > self.timeout:
                    return []
                new_row = self.apply_decoding_strategies(row)
                if new_row is not None:
                    new_pixel_matrix.append(new_row)
        return new_pixel_matrix

    def apply_decoding_strategies(self, row):
        """
            Applies a combination of dilation and row splitting
        """
        new_row = self.reduce_row(row)
        valid_rows = set()
        if len(new_row) != self.bits_count or not parity_check(new_row):
            valid_rows |= self.bfs_find(row)
            if len(list(valid_rows)) == 0:
                row = self.apply_dilation(row)
                valid_rows |= self.bfs_find(row)
                if len(list(valid_rows)) == 0:
                    print('ERROR ERROR')
        else:
            valid_rows.add(new_row)
        return list(valid_rows)

    def reduce_row(self, row):
        """
            Performs the row decoding:
            - Determine color area sizes
            - If smallest size = 1 --> Noise --> apply dilation
            - Determine areas which are two units wide
            - Check for three unit wide area
            - Return new decoded row
        """
        sizes = self.determine_color_area_sizes(row)
        sorted_sizes = sorted(sizes, key=lambda k: k['size'])
        while sorted_sizes[0]['size'] == 1:
            row = self.apply_dilation(row)
            sizes = self.determine_color_area_sizes(row)
            sorted_sizes = sorted(sizes, key=lambda k: k['size'])

        double_units = int(self.bits_count - len(sorted_sizes))
        epsilon, triple_white = self.get_epsilon(row, double_units, sorted_sizes)
        if epsilon is None and triple_white is None:
            return ''
        return self.create_new_row(sizes, epsilon, row, triple_white)

    def apply_dilation(self, row):
        """
            Converts the row so that the dilation operation can be applied
        """
        img = self.create_numpy_row(row)
        binary_img = self.dilate_numpy_row(img)
        return self.create_binary_row(binary_img, row)

    def dilate_numpy_row(self, img):
        """
            Performs dilation with a 2x2 kernel and 2 iterations
        """
        kernel = np.ones((2, 2), np.uint8)
        inverted = cv2.bitwise_not(img)
        dilation = cv2.dilate(inverted, kernel, iterations=2)
        img = cv2.bitwise_not(dilation)
        img = cv2.dilate(img, kernel, iterations=1)
        _, binary_img = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)
        return binary_img

    def create_numpy_row(self, row):
        """
            Converts a row to a numpy array and use a three dimensional
            vector to represent the color.
        """
        img_row = np.zeros((len(row), len(row[0]['row']), 3), np.uint8)
        for row_index, row2 in enumerate(row):
            for col_index, col in enumerate(row2['row']):
                if col == 1:
                    img_row[row_index, col_index] = (0, 0, 0)
                elif col == 0:
                    img_row[row_index, col_index] = (255, 255, 255)
        return img_row

    def create_binary_row(self, binary_img, row):
        """
            Converts a row with three dimensional color values
            to a binary row  (only black/white)
        """
        rows, columns, _ = binary_img.shape
        pixel = 0
        new_rows = []
        new_row = []
        for i in range(rows):
            for j in range(columns):
                pixel = binary_img[i, j]
                if pixel[0] == 0:
                    new_row.append(1)
                elif pixel[0] == 255:
                    new_row.append(0)
            new_rows.append(new_row)
            new_row = []
        dilated_row = copy.deepcopy(row)
        for i in range(len(new_rows)):
            dilated_row[i]['row'] = new_rows[i]
        return dilated_row

    def determine_color_area_sizes(self, row):
        sizes = []
        size = 0
        last_value = 1
        pos = 0
        for i in range(len(row[0]['row'])):
            value = self.determine_column_color(row, i)
            if value == last_value:
                size += 1
            else:
                sizes.append({'pos': pos, 'size': size, 'value': last_value})
                size = 1
                pos += 1
            last_value = value
        sizes.append({'pos': pos, 'size':size, 'value': last_value})
        return sizes

    def determine_column_color(self, row, index):
        """
            Most common pixel color determines the column color
        """
        pixels = []
        for single_row in row:
            if single_row['pattern'] == WHITE_BLACK_PATTERN:
                single_row = self.extend_rack(single_row)
            pixels.append(single_row['row'][index])
        counter = Counter(pixels)
        return counter.most_common(1)[0][0]

    def extend_rack(self, row):
        """
            Scans row from right to left and replaces all white pixels
            with black pixels until a black pixel is found
        """
        for j in range(len(row['row'])):
            if row['row'][len(row['row']) - j - 1] == 0:
                row['row'][len(row['row']) - j - 1] = 1
            else:
                return row

    def get_epsilon(self, row, double_units, sorted_sizes):
        triple_unit = False
        offset = 0
        if row[0]['pattern'] == WHITE_BLACK_PATTERN:
            double_units -= 2
            offset += 1
            # rack has 3 black units, check second widest color area has the same size
            # or that second widest area is at least 2 pixels wieder than the third widest
            # area
            if sorted_sizes[-2]['size'] == sorted_sizes[-1]['size'] or abs(sorted_sizes[-2]['size'] - sorted_sizes[-3]['size']) >= 2:
                double_units -= 2
                triple_unit = True
                offset += 1
        elif row[0]['pattern'] == BLACK_WHITE_PATTERN:
            # rack has only two black units so check if widest area is at least 2 pixels wider than
            # the second widest
            if abs(sorted_sizes[-1]['size'] - sorted_sizes[-2]['size']) >= 2:
                double_units -= 2
                triple_unit = True
                offset += 1
        if len(sorted_sizes) < (-1*double_units - offset) * -1:
            return None, None
        return sorted_sizes[-1*double_units - offset]['size'], triple_unit

    def create_new_row(self, sizes, epsilon, row, triple_white):
        new_row = ''
        for k, item in enumerate(sizes):
            if item['size'] < epsilon:
                new_row += str(item['value'])
            elif row[0]['pattern'] == WHITE_BLACK_PATTERN and k == len(sizes) - 1:
                new_row += str(item['value'])
                new_row += str(item['value'])
                new_row += str(item['value'])
            elif row[0]['pattern'] == WHITE_BLACK_PATTERN and triple_white and k == (len(sizes) - 1 - 1):
                new_row += str(item['value'])
                new_row += str(item['value'])
                new_row += str(item['value'])
            elif row[0]['pattern'] == BLACK_WHITE_PATTERN and triple_white and k == (len(sizes) - 1 - 2):
                new_row += str(item['value'])
                new_row += str(item['value'])
                new_row += str(item['value'])
            else:
                new_row += str(item['value'])
                new_row += str(item['value'])
        return new_row

    def bfs_find(self, row, valid_rows=set()):
        """
            Rows are split with a BFS search.
            All valid rows are returned
        """
        explored = []
        queue = [row]

        while queue:
            node = queue.pop(0)
            if node not in explored:
                explored.append(node)
                if len(node) > 0:
                    reduced = self.reduce_row(node)
                    if len(reduced) == self.bits_count and parity_check(reduced):
                        valid_rows.add(reduced)
                    top = node[0:round(len(node)/2)]
                    bottom = node[round(len(node)/2):]
                    queue.append(top)
                    queue.append(bottom)
        return valid_rows
