import numpy as np
import scipy.misc

from Utils import load_cnn

MODEL_FILENAME = "nn/models/row_extractor.json"
WEIGHT_FILENAME = "nn/models/row_extractor.hdf5"
LABELS_FILENAME = "nn/models/row_extractor.dat"

ROW_HEIGHT = 10
ROW_WINDOW = [20, 10]


class CnnRowExtractor:
    """
        Extracts the rows from a Cauzin Softstrip with the help of
        a CNN. A window is slid along the Softstrip and the CNN
        decides the point to split this window into two rows.
    """
    def __init__(self, grayscale_matrix, binary_matrix, bits_per_row):
        self.grayscale_matrix = grayscale_matrix
        self.binary_matrix = binary_matrix
        self.bits_per_row = bits_per_row
        self.model, self.labels = load_cnn(MODEL_FILENAME, WEIGHT_FILENAME, LABELS_FILENAME)

    def extract_rows(self):
        """
            Extracts the rows from a Cauzin Softstrip and returns
            a matrix with grayscale rows and a matrix with binary rows
        """
        binary_rows = []
        grayscale_rows = []
        last_end = 0
        unit_width = len(self.grayscale_matrix[0]) / self.bits_per_row
        start = 0
        while start < len(self.grayscale_matrix):
            grayscale_pixel_lines, binary_pixel_lines = self.extract_rows_with_window(start)
            img = self.apply_row_window(grayscale_pixel_lines, unit_width)
            if img.any():
                prediction = self.predict_split_point(img)
                split_point = self.labels.inverse_transform(prediction)[0]

                grayscale_rows.append(grayscale_pixel_lines[0:split_point])
                binary_rows.append(binary_pixel_lines[0:split_point])

                last_end = start + split_point
                start = last_end
            else:
                start = len(self.grayscale_matrix)

        return grayscale_rows, binary_rows

    def extract_rows_with_window(self, start):
        """
            Returns the rows which are inside the current
            window position.
        """
        end = round(start + ROW_HEIGHT * 2)
        if end > (len(self.grayscale_matrix) - 1):
            end = len(self.grayscale_matrix) - 1
        grayscale_rows = self.grayscale_matrix[start:end]
        binary_rows = self.binary_matrix[start:end]
        return grayscale_rows, binary_rows

    def apply_row_window(self, rows, bit_width):
        """
            Returns the values inside the current window
            position.
        """
        window = []
        cb_start = int(round(bit_width * 3))
        cb_end = int(round(bit_width * 5))

        for row in rows:
            window.append(row[cb_start:cb_end])

        return np.array(window)

    def predict_split_point(self, window):
        """
            Feeds the row window into the CNN and
            return the predicted value.
        """
        resized = scipy.misc.imresize(window, ROW_WINDOW)
        resized = np.expand_dims(resized, axis=2)
        resized = np.expand_dims(resized, axis=0)
        resized = resized / 255.0
        return self.model.predict(resized)