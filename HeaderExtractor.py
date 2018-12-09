from AbstractHeaderExtractor import AbstractHeaderExtractor
from RowComponents import RowComponents
from math import sqrt

HORIZONTAL_SYNC_DELTA = 0.1
HORIZONTAL_SIMILARITY_MINIMUM = 5
VERTICAL_SIMILARITY_MINIMUM = 3
MINIMUM_BAR_DIFFERENCE = 10
class HeaderExtractor(AbstractHeaderExtractor):
    """
        Implementation of AbstractHeaderExtractor
        - Determines the number of bytes in a row
        - Removes the horizontal synchronization section
    """
    def __init__(self, softstrip_matrix):
        """
            Constructor
            Parameters
            ----------
            softstrip_matrix: SoftstripMatrix
        """
        self.nibbles = 0
        self.softstrip_matrix = softstrip_matrix
        self.create_components()

    def remove_horizontal_header(self):
        vertical_sync_start = self.parse_header()
        self.remove_horizontal_header_from_matrix(vertical_sync_start)
        return self.softstrip_matrix


    def parse_header(self):
        """
            Determines the number of nibbles per row and finds the start index
            of the vertical synchronization section
        """
        horizontal_sync_extracted = False
        vertical_sync_extracted = False
        for index, row in enumerate(self.components):
            if not horizontal_sync_extracted:
                if self.check_row_similarity(index, HORIZONTAL_SIMILARITY_MINIMUM):
                    self.nibbles = self.decode_nibbles(row)
                    horizontal_row = row
                    horizontal_sync_extracted = True
            if horizontal_sync_extracted and not vertical_sync_extracted:
                vertical_sync_start = index
                count_diff = abs(len(row['components']) - len(horizontal_row['components']))
                if count_diff > MINIMUM_BAR_DIFFERENCE:
                    if self.check_row_similarity(index, VERTICAL_SIMILARITY_MINIMUM):
                        vertical_sync_extracted = True
                        vertical_sync_row = row
        return vertical_sync_start

    def remove_horizontal_header_from_matrix(self, vertical_sync_start):
        """
            Deletes all rows before vertical_sync_start
        """
        for i in range(vertical_sync_start):
            del self.softstrip_matrix.binary_matrix[0]
            if self.softstrip_matrix.grayscale_matrix is not None:
                del self.softstrip_matrix.grayscale_matrix[0]  

    def get_bits_per_row(self):
        """
            Calculates the number of bits per row.
            The constant 14 consists of:
                - 2 bits for left start bar
                - 1 bit space after the start bar
                - 2 bit checkerboard
                - 2 bit for parity (left)
                - 2 bit for parity (right)
                - 2 bit space after right parity (or 1)!
                - 3 bit for right alignment (or 2)!
        """
        return 14 + self.nibbles * 8 


    def check_row_similarity(self, current_row_index, no_of_rows):
        """
            Checks if the following rows are similar to the current one.
            Parameters
            ----------
            current_row_index:
                                The current row which is compared to other rows.
            no_of_rows:
                                The number of following rows which are compared
                                to the current row.
        """
        distances = []
        for i in range(no_of_rows):
            distance = self.calculate_euclidean_distance(self.components[current_row_index], 
                                                         self.components[current_row_index + i])
            distances.append(distance)
        equal = True
        for distance in distances:
            if distance >= HORIZONTAL_SYNC_DELTA:
                equal = False
        return equal

    def calculate_euclidean_distance(self, line_1, line_2):
        """
            Calculates the similarity between two pixel lines,
            The features for measuring the similarity are:
            - maximum bar size
            - maximum bar size
            - average bar size
            - number of bars
        """
        keys = ['max_size', 'min_size', 'avg_size', 'count']
        dist = 0
        for key in keys:
            dist += (line_1[key] - line_2[key])**2
        return sqrt(dist)

    def decode_nibbles(self, row):
        """
            Counts the white to black transitions to decode the
            number of nibbles per row.
        """
        transitions = 0
        last_value = -1
        for component in row['components']:
            if last_value == 0 and component['value'] == 1:
                transitions += 1
            last_value = component['value']
        nibbles = (transitions + 5) / 2 # 5 because first 0 component is removed

        return nibbles

    def create_components(self):
        """
            Creates the 'row-components'.
            The following information are collected for each pixel line:
            - maximum bar width
            - minimum bar width
            - average bar width
            - number of bars
            - the pixels of each bar
        """
        row_components = RowComponents(self.softstrip_matrix.binary_matrix)
        self.components = row_components.components