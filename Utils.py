import pickle
from keras.models import model_from_json

# Constants for checkerboard-rack pattern
# Example:
# WHITE_WHITE: first square of checkerboard = white
#              last square of rack = white
WHITE_WHITE_PATTERN = 0
WHITE_BLACK_PATTERN = 1
BLACK_WHITE_PATTERN = 2
BLACK_BLACK_PATTERN = 3


def convert_dibit_to_bit(dibit):
    if dibit == '10':
        return 0
    elif dibit == '01':
        return 1
    else:
        return 0


def convert_dibit_row_to_bit(row):
    bit_row = list()
    while row:
        dibit = row[0:2]
        bit_row.append(convert_dibit_to_bit(dibit))
        row = row[2:]
    return bit_row


def convert_int_to_dibit(value):
    if value == 0:
        return '10'
    elif value == 1:
        return '01'


def calculate_parity(data):
    converted_data_line = convert_dibit_row_to_bit(data)
    computed_left_parity = sum(converted_data_line[1::2]) % 2
    computed_right_parity = sum(converted_data_line[::2]) % 2
    return convert_int_to_dibit(computed_left_parity), convert_int_to_dibit(computed_right_parity)


def parity_check(row):
    data = row[7:-7]
    converted_data_line = convert_dibit_row_to_bit(data)
    computed_left_parity = sum(converted_data_line[1::2]) % 2
    computed_right_parity = sum(converted_data_line[::2]) % 2
    left_parity = convert_dibit_to_bit(row[5:7])
    right_parity = convert_dibit_to_bit(row[-7:-5])
    if computed_left_parity != left_parity or computed_right_parity != right_parity:
        return False
    return True


def pop_multiple_items(list, start, end):
    items = list[start:end]
    del list[start:end]
    return items


def load_cnn(model_filename, weight_filename, label_filename):
    """
        Configures the CNN:
        - Loads model
        - Loads weights
        - Loads labels
    """
    with open(label_filename, 'rb') as f:
        labels = pickle.load(f)
        json_file = open(model_filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights(weight_filename)
    return model, labels