from Utils import *
SEGMENT_SIZE = 75
MIN_OCCURENCE = 6


class AlgorithmicRowExtractor:
    """
        Uses the checkerboard and rack pattern to extract
        all rows in a Cauzin Softstrip.
    """

    def __init__(self, softstrip_matrix, bits_per_row):
        self.softstrip_matrix = softstrip_matrix
        self.bits_per_row = bits_per_row

    def extract_rows(self):
        boundaries = self.determine_matrix_boundaries()
        pattern_pixel_matrix = self.determine_pattern_per_line(boundaries)
        return self.group_by_pattern(pattern_pixel_matrix)

    def determine_matrix_boundaries(self):
        """
            Divides the Softstrip into multiple segments and determines for
            each segment:
                - Min/max of the start/end positions of the left black
                  checkerboard square
                - Min/max of the start/end position of the last black rack
                  square
            Instead of determining the min/max values for the whole softstrip,
            it is determined for multiple segments to increase the accuracy.
        """
        segments = int(len(self.softstrip_matrix.binary_matrix) / SEGMENT_SIZE)
        start = 0
        boundaries = []

        for index, row in enumerate(self.softstrip_matrix.binary_matrix):
            if index % segments == 0 and start != index:
                if (len(self.softstrip_matrix.binary_matrix) - index) <= segments:
                    boundary = self.determine_segment_boundaries(start, len(self.softstrip_matrix.binary_matrix))
                else:
                    boundary = self.determine_segment_boundaries(start, index)
                boundaries.append(boundary)
                start = index
        return boundaries

    def determine_segment_boundaries(self, start, end):
        """
            Determines for the segment (start-end):
            - Min/max of the start/end positions of the left black
                  checkerboard square
            - Min/max of the start/end position of the last black rack
                  square
            Parameters
            ----------
            start:int
                        Start of segment
            end:int
                        End of segment
        """
        checkerboard_boundaries, rack_boundaries = self.determine_cb_and_rack_boundaries(start, end)
        filtered_checkerboard_boundaries= self.filter_checkerboard_outliers(checkerboard_boundaries, start)
        filtered_rack_boundaries = self.filter_rack_outliers(rack_boundaries)
        return {
            'start': start,
            'end': end,
            'min_left_start': min(filtered_checkerboard_boundaries),
            'max_left_end': max(filtered_checkerboard_boundaries),
            'min_right_end': min(filtered_rack_boundaries),
            'max_right_end': max(filtered_rack_boundaries)
        }

    def filter_checkerboard_outliers(self, checkerboard_boundaries, start):
        """
            Removes all positions outside a defined checkerboard window and
            all positions which occur less than MIN_OCCURENCE

            Parameters
            ----------
            checkerboard_boundaries:
                                        unfiltered positions of the black square
                                        of the  checkerboard
            start:
                                        start of the segment
        """
        filtered_checkerboard_boundaries = set()
        # 0.5 * dibit width
        bit_width = (len(self.softstrip_matrix.binary_matrix[start]) / self.bits_per_row)
        # rough window around the checkerboard
        # pixels in checkerboard_boundary must be within this window
        cb_start = bit_width * 2.25
        cb_end = bit_width * 4.25
        for item in checkerboard_boundaries:
            if item > cb_start and item < cb_end:
                if checkerboard_boundaries.count(item) >= MIN_OCCURENCE:
                    filtered_checkerboard_boundaries.add(item)
        return list(filtered_checkerboard_boundaries)

    def filter_rack_outliers(self, rack_boundaries):
        """
           Remove all positions which occur less than MIN_OCCURENCE
        """
        filtered_rack_boundaries = set()
        for item in rack_boundaries:
            if rack_boundaries.count(item) >= MIN_OCCURENCE:
                filtered_rack_boundaries.add(item)
        return list(filtered_rack_boundaries)

    def determine_cb_and_rack_boundaries(self, start, end):
        """
            Determines the the positions of the black checkerboard square
            and the position of the black rack square
            Parameters
            ----------
            start:
                        start of the segment
            end:
                        end of the segment
        """
        checkerboard_boundary = []
        rack_boundary = []
        for row_index in range(start, end):
            row = self.softstrip_matrix.binary_matrix[row_index]
            black_counter = 0
            last_pixel = 0
            # Find the left black start of the checkerboard
            # and store the number of black pixels
            for column_index, column in enumerate(row):
                if column == 1 and last_pixel == 0:
                    black_counter += 1
                    if black_counter == 2:
                        checkerboard_boundary.append(column_index)
                        break
                last_pixel = column
            # Find the first black pixel from right-to-left
            for column_index, column in enumerate(reversed(row)):
                if column == 1:
                    rack_boundary.append(len(row) - column_index - 1)
                    break
        return checkerboard_boundary, rack_boundary

    def determine_pattern_per_line(self, boundaries):
        """
            Determines the checkerboard pattern (black-white or white-black)
            and the last rack square (white or black)

            Returns a new matrix with the following row structure:
            Pattern | Index | Row
        """
        pattern_matrix = []
        boundary = boundaries.pop(0)
        for index, row in enumerate(self.softstrip_matrix.binary_matrix):
            if index >= boundary['end']:
                boundary = boundaries.pop(0)
            # The left square of the checkerboard is interesting, substract -1 to increase the chance of hitting it
            checkerboard = round(boundary['min_left_start'] + (boundary['max_left_end'] - boundary['min_left_start']) * 0.5)
            rack = round(boundary['min_right_end'] + (boundary['max_right_end'] - boundary['min_right_end']) * 0.5)

            if (row[checkerboard] == 1 or (row[checkerboard - 1] == 1 and row[checkerboard - 2] == 1)) and row[rack] == 0:
                pattern = BLACK_WHITE_PATTERN
            elif row[checkerboard] == 0 and row[rack] == 0:
                pattern = WHITE_WHITE_PATTERN
            elif row[checkerboard] == 0 and row[rack] == 1:
                pattern = WHITE_BLACK_PATTERN
            elif row[checkerboard] == 1 and row[rack] == 1:
                pattern = BLACK_BLACK_PATTERN
            pattern_matrix.append({'pattern': pattern, 'index': index, 'row': row})

        return pattern_matrix
    
    def group_by_pattern(self, pattern_pixel_matrix):
        """
            Grouping lines with the samer pattern
            ==> Rows are created
        """
        current_pattern = BLACK_WHITE_PATTERN
        next_pattern = WHITE_BLACK_PATTERN
        grouped_binary_matrix = []
        grouped_binary_row = []
        grouped_grayscale_matrix = []
        grouped_grayscale_row = []
        for index, row in enumerate(pattern_pixel_matrix):
            if row['pattern'] == current_pattern:
                grouped_binary_row.append(row)
                grouped_grayscale_row.append(self.softstrip_matrix.grayscale_matrix[index])
            elif row['pattern'] == next_pattern:
                grouped_binary_matrix.append(grouped_binary_row)
                grouped_binary_row = []
                grouped_binary_row.append(row)

                grouped_grayscale_matrix.append(grouped_grayscale_row)
                grouped_grayscale_row = []
                grouped_grayscale_row.append(self.softstrip_matrix.grayscale_matrix[index])
                next_pattern = current_pattern
                current_pattern = row['pattern']
        grouped_binary_matrix.append(grouped_binary_row)

        grouped_grayscale_matrix.append(grouped_grayscale_row)
        return grouped_binary_matrix, grouped_grayscale_matrix
