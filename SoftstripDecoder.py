import sys
import cv2
import datetime
import yaml
import argparse
import os

from DataExtractor import DataExtractor
from HeaderExtractor import HeaderExtractor
from SoftstripMatrix import SoftstripMatrix
from CnnRowExtractor import CnnRowExtractor
from AlgorithmicRowExtractor import AlgorithmicRowExtractor
from CnnRowDecoder import CnnRowDecoder
from AlgorithmicRowDecoder import AlgorithmicRowDecoder

CONFIG_FILENAME = 'config.yaml'
CNN_ROW_DECODER = 1
ALGO_ROW_DECODER = 0
CNN_ROW_EXTRACTOR = 1
ALGO_ROW_EXTRACTOR = 0


class SoftstripDecoder:
    """
        Starts the decoding pipeline
    """
    def __init__(self, imgs, paths=[], gray_imgs=[]):
        """
            Decodes the Cauzin Softstrip:
            imgs: array with binary images
            paths: paths for the images
            gray_imgs: grayscale images
        """
        self.load_config()
        self.data = []
        self.start_time = datetime.datetime.now().replace(microsecond=0)
        for i in range(len(imgs)):
            path = paths.pop(0)
            gray_img = gray_imgs.pop(0)
            img = imgs.pop(0)
            self.gray_img = gray_img
            self.path = path
            if i == 0:
                self.decode(img, True)
            else:
                self.decode(img, False)
        self.save_data()

    def load_config(self):
        self.config = open(CONFIG_FILENAME, 'r')
        self.config = yaml.load(self.config)

    def save_data(self):
        fn = self.strip_meta_info.filename
        print("SAVE: " + str(len(self.data)) + " BYTES AS " + fn)
        if "/" in fn:
            os.makedirs(os.path.dirname(fn), exist_ok=True)
        with open(self.strip_meta_info.filename, mode='wb') as f:
            f.write(bytearray(self.data))

    def decode(self, img, first_strip=False):
        softstrip_matrix = SoftstripMatrix(img, self.gray_img)
        header_extractor = HeaderExtractor(softstrip_matrix)
        header_extractor.parse_header()
        vertical_sync_start = header_extractor.vertical_sync_start
        self.bits_count = header_extractor.get_bits_per_row()

        if self.config['row_extractor'] == CNN_ROW_EXTRACTOR:
            row_extractor = CnnRowExtractor(softstrip_matrix.grayscale_matrix, softstrip_matrix.binary_matrix, self.bits_count)
            gray_grouped_matrix, grouped_matrix = row_extractor.extract_rows()
        else:
            row_extractor = AlgorithmicRowExtractor(softstrip_matrix, self.bits_count)
            grouped_matrix, gray_grouped_matrix = row_extractor.extract_rows()

        if self.config['row_decoder'] == CNN_ROW_DECODER:
            row_decoder = CnnRowDecoder(gray_grouped_matrix, self.start_time, self.bits_count, self.config['timeout'], vertical_sync_start)
            reduced_pixel_matrix = row_decoder.decode_rows()
        else:
            row_decoder = AlgorithmicRowDecoder(grouped_matrix, self.bits_count, self.start_time, self.config['timeout'])
            reduced_pixel_matrix = row_decoder.decode_rows()

        if len(reduced_pixel_matrix) == 0:
            print('[ERROR] ' + self.path + ' is invalid!')
        else:
            data_extractor = DataExtractor(self.config['timeout'])
            data_extractor.extract_data(reduced_pixel_matrix, first_strip, self.start_time)

            self.data += data_extractor.data

            
            if data_extractor.valid:
                print('Checksum valid!')
                if first_strip:
                    self.strip_meta_info = data_extractor.file_header
                    print(self.strip_meta_info)
            else:
                print('Checksum invalid!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Softstrip Decoder')
    parser.add_argument('paths', nargs='+')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    binary_imgs = []
    gray_imgs = []
    paths = []
    strips = []
    args = parser.parse_args()
    for file in args.paths:
        img = cv2.imread(file)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        binary_imgs.append(binary_img)
        gray_imgs.append(gray_img)
        paths.append(file)
    print(paths)
    try:
        decoder = SoftstripDecoder(imgs=binary_imgs, paths=paths, gray_imgs=gray_imgs)
    except Exception as e:
        print(e)
