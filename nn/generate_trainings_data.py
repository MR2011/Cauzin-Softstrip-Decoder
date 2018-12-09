import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from SoftstripEncoder import *
import cv2
import numpy as np

def create_rgb_matrix(row):
    rgb_matrix = np.zeros((len(row), len(row[0]), 3), np.uint8)
    for row_index, single_row in enumerate(row):
        rgb_row = []
        for col_index, col in enumerate(single_row):
            if col == '1':
                rgb_matrix[row_index, col_index] = (0, 0, 0)
            else:
                rgb_matrix[row_index, col_index] = (255, 255, 255)
    return rgb_matrix

def create_gray_matrix(row):
    gray_matrix = np.zeros((len(row), len(row[0]),1), np.uint8)
    for row_index, single_row in enumerate(row):
        gray_row = []
        for col_index, col in enumerate(single_row):
            gray_matrix[row_index, col_index] = col
    return gray_matrix

def create_trainings_data(reduced_path, rows_path, save_path):
    row = []
    line_count = 0
    with open(reduced_path, 'r') as reduced_file:
        gray_rows = []
        with open(rows_path, 'r') as row_file:
            for row_line in row_file:   
                row_line = row_line.strip()
                if row_line == '':
                    reduced_line = reduced_file.readline()
                    reduced_line = reduced_line.strip()
                    cv2.imwrite(save_path + str(line_count) + '_' + reduced_line + '.png', create_gray_matrix(gray_rows))
                    gray_rows = []
                    line_count += 1
                else:
                    row_line = row_line[1:-1]
                    gray_rows.append(list(map(int, row_line.split(','))))



create_trainings_data('textfiles/qwiksort1_reduced.txt', 'textfiles/qwiksort1_gray_rows.txt', 'data/first_strip_train/')
create_trainings_data('textfiles/fspath1_reduced.txt', 'textfiles/fspath1_gray_rows.txt', 'data/first_strip_train/')
create_trainings_data('textfiles/linklist1_reduced.txt', 'textfiles/linklist1_gray_rows.txt', 'data/first_strip_train/')
create_trainings_data('textfiles/muldirec1_reduced.txt', 'textfiles/muldirec1_gray_rows.txt', 'data/first_strip_train/')
create_trainings_data('textfiles/valpost1_reduced.txt', 'textfiles/valpost1_gray_rows.txt', 'data/first_strip_train/')
