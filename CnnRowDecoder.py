import datetime
import numpy as np
import scipy.misc
import itertools
from Utils import *

MODEL_FILENAME = 'nn/models/decoding_simple.json'
WEIGHT_FILENAME = 'nn/models/decoding_simple.hdf5'
LABELS_FILENAME = 'nn/models/decoding_simple.dat'
SHIFT_OFFSETS = [0, 1, -1,  2, -2]
MIN_CONFIDENCE = 0.9


class CnnRowDecoder:
    """
        Implementation of a row decoding method with a CNN.
        The dibits in each row are classified with a CNN.
    """
    def __init__(self, grayscale_grouped_matrix, start_time, bits_count, timeout):
        self.grayscale_grouped_matrix = grayscale_grouped_matrix
        self.start_time = start_time
        self.bits_count = bits_count
        self.model, self.labels = load_cnn(MODEL_FILENAME, WEIGHT_FILENAME, LABELS_FILENAME)
        self.timeout = timeout

    def decode_rows(self):
        """
            Decodes the dibits in all rows of the grayscale_grouped_matrix
        """
        return self.reduce_grayscale_grouped_matrix(self.grayscale_grouped_matrix)

    def reduce_grayscale_grouped_matrix(self, matrix):
        """
            Decodes the dibits in all rows of the grayscale_grouped_matrix
        """
        reduced_matrix = []
        for index, row in enumerate(matrix):
            # Used for Timeout after X minutes
            now = datetime.datetime.now().replace(microsecond=0)
            difference = now - self.start_time
            if (difference.seconds // 60) > self.timeout:
                return []

            # Ignore empty rows
            if len(row) > 0:
                valid_rows = set()
                # Row shifting
                for offset in SHIFT_OFFSETS:
                    new_rows, first_try = self.apply_decoding_strategies(row, offset, valid_rows)
                    valid_rows |= new_rows
                    # Stop if row was succesffuly decoded on first try
                    if first_try:
                        break

                valid_rows = list(valid_rows) 
                if len(valid_rows) == 0: # Row could not be decoded
                    print("INDEX:" + str(index))
                    print("NO VALID ROW FOUND")
                    return []
                else:
                    reduced_matrix.append(valid_rows)
        return reduced_matrix

    def apply_decoding_strategies(self, row, offset, valid_rows):
        """
            Decodes the dibits in a row. If if failed:
            - Change dibits with low confidence
            - Split rows with BFS
        """
        decoded_row, confidences = self.predict_dibits(row, offset)
        if not parity_check(decoded_row):
            valid_rows |= self.change_uncertain_dibits(decoded_row, confidences)
            valid_rows |= self.bfs_find(row, valid_rows, offset)
            return valid_rows, False
        else:
            valid_rows.add(decoded_row)
            return valid_rows, True

    def change_uncertain_dibits(self, row, confidences):
        """
            Changes the dibit values in a row which have a low
            confidence value and checks whether they are valid
            or not.
            Returns all valid rows which were found.
        """
        valid_rows = set()
        combinations, uncertain = self.determine_dibit_flip_combinations(confidences)
        for combination in combinations:
            split_row = list(row)
            for pos, value in zip(uncertain, combination):
                if value == 1:
                    if split_row[pos * 2 + 5] == '0':
                        split_row[pos * 2 + 5] = '1'
                        split_row[pos * 2 + 6] = '0'
                    else:
                        split_row[pos * 2 + 5] = '0'
                        split_row[pos * 2 + 6] = '1'
            joined_row = ''.join(split_row)
            if parity_check(joined_row):
                valid_rows.add(joined_row)
        return valid_rows

    def determine_dibit_flip_combinations(self, confidences):
        """
            Determines dibits with a low confidence value (< MIN_CONFIDENCE)
            and returns all flipping combinations. 
            The combinations are sorted so that first only a single dibit is
            changed and later more dibits.
        """
        uncertain = []
        for index, value in enumerate(confidences):
            if value < MIN_CONFIDENCE:
                uncertain.append(index)
        combinations = list(itertools.product([0, 1], repeat=len(uncertain)))
        # sort combinations:
        # (0, 0, 0, 0, 1), (0, 0, 0, 1, 0), (0, 0, 1, 0, 0) ...
        #  so that only one dibit is changed first
        return sorted(combinations, key=lambda x: x.count(1)), uncertain

    def bfs_find(self, row, valid_rows=set(), offset=0):
        """
            Rows are split with a BFS search. If the decoding of a split
            row fails, the dibits with a low confidence value will be changed.
            Returns all valid rows which were found
        """
        explored = []
        queue = [row]
        while queue:
            node = queue.pop(0)
            if node not in explored:
                explored.append(node)
                if len(node) > 0:
                    reduced, confidences = self.predict_dibits(node, offset)
                    if parity_check(reduced):
                        valid_rows.add(reduced)
                    else:
                        confidence_rows = self.change_uncertain_dibits(reduced, confidences)
                        if len(confidence_rows) > 0:
                            valid_rows |= confidence_rows
                    top = node[0:round(len(node)/2)]
                    bottom = node[round(len(node)/2):]
                    queue.append(top)
                    queue.append(bottom)
        return valid_rows

    def predict_dibits(self, row, offset=0):
        """
            Classifies each dibit in a row
        """
        new_row = ''
        np_row = np.array(row)
        confidences = []

        for i in range(int((self.bits_count - 10) / 2)):
            prediction = self.predict_dibit(np_row, i, offset)
            label = self.labels.inverse_transform(prediction)[0]
            confidences.append(self.parse_confidence(prediction))
            new_row += str(label)

        return '11010' + new_row + '00110', confidences

    def predict_dibit(self, row, index, offset):
        """
            Classifies a single dibit
        """
        img_height, img_width = row.shape
        block_width = img_width / self.bits_count
        skipped = block_width * 5
        start = int(round(skipped + index * block_width * 2 + offset))
        end = int(round(start + block_width * 2 + offset))
        dibit = row[0:img_height, start:end]
        dibit = scipy.misc.imresize(dibit, [20, 20])
        dibit = np.expand_dims(dibit, axis=2)
        dibit = np.expand_dims(dibit, axis=0)
        dibit = dibit / 255.0
        return self.model.predict(dibit)

    def parse_confidence(self, prediction):
        value = prediction[0][0]
        if value <= 0.5:
            confidence = 1.0 - value
        else:
            confidence = 0 + value
        return confidence
