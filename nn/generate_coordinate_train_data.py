import numpy as np
import json
import cv2

OUTPUT_PATH = 'data/row_manual_left/'


def parse_grouped_rows_file(grouped_rows_path):
    row_matrix = []
    row = []
    with open(grouped_rows_path, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                line = line.replace("'", "\"")
                json_line = json.loads(line)
                row.append(json_line)
            else:
                row_matrix.append(row)
                row = []
    return row_matrix

def parse_gray_matrix_file(gray_matrix_path):
    gray_matrix = []
    with open(gray_matrix_path, 'r') as f:
        for line in f:
            line = line.strip()
            line = line[1:-1]
            gray_matrix.append(list(map(int, line.split(','))))
    return gray_matrix

def parse_binary_matrix_file(binary_matrix_path):
    i = 0
    split_indices = []
    with open(binary_matrix_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                split_indices.append(i)
                i = 0
            else:
                i += 1
    return split_indices

def generate_training_data(gray_matrix, row_matrix, bits_per_row, strip_name, use_manual_split=False):
    row_height = 10
    grouped_rows = []
    last_end = 0
    number_of_rows = 0
    bit_width = len(gray_matrix[0]) / bits_per_row
    start = 0
    while start < len(gray_matrix):
        end = round(start + row_height * 2)
        if end >= len(gray_matrix):
            end = len(gray_matrix) - 1
        rows = gray_matrix[start:end]
        row = []
        left_start = int(round(bit_width * 3))
        left_end = int(round(bit_width * 5))
        for r in rows:
            row.append(r[left_start:left_end])

        if number_of_rows >= len(row_matrix):
                break
        if use_manual_split:
            split = row_matrix[number_of_rows]
            row_end = start + split
        else:
            row_end = min(end, row_matrix[number_of_rows][-1]['index'])
            split = row_end - start
        grouped_rows.append(rows[0:split])
        cv2.imwrite(OUTPUT_PATH + strip_name + str(number_of_rows) + '_' + str(split) + '.png', np.array(row))

        number_of_rows += 1
        last_end = row_end
        start = last_end
    return grouped_rows

def print_grouped_rows(grouped_rows):
    for row in grouped_rows:
        for single_row in row:
            print(single_row)
        print('')

def parse_strip(gray_matrix_path, grouped_rows_path, bits_per_row):
    row_matrix = parse_grouped_rows_file(grouped_rows_path)
    gray_matrix = parse_gray_matrix_file(gray_matrix_path)
    strip_name = gray_matrix_path.split('/')[1].split('_')[0]
    generate_training_data(gray_matrix, row_matrix, bits_per_row, strip_name)

def parse_strip_with_manual_split(binary_matrix_path, gray_matrix_path, bits_per_row):
    gray_matrix = parse_gray_matrix_file(gray_matrix_path)
    split_indices = parse_binary_matrix_file(binary_matrix_path)
    strip_name = gray_matrix_path.split('/')[1].split('_')[0]
    grouped_rows = generate_training_data(gray_matrix, split_indices, bits_per_row, strip_name, True)


parse_strip_with_manual_split('textfiles/qwiksort1_rows_by_hand.txt', 'textfiles/qwiksort1_gray_matrix.txt', 78)
parse_strip_with_manual_split('textfiles/valpost3_rows_by_hand.txt', 'textfiles/valpost3_gray_matrix.txt', 78)
parse_strip_with_manual_split('textfiles/fspath8_rows_by_hand.txt', 'textfiles/fspath8_gray_matrix.txt', 78)
parse_strip_with_manual_split('textfiles/muldirec6_rows_by_hand.txt', 'textfiles/muldirec6_gray_matrix.txt', 78)
