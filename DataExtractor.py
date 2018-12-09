import itertools
import datetime
from Utils import *
from DataFieldHelper import parse_length
from FileHeader import FileHeader


class DataExtractor:
    """
        Extracts and parses all file information fields and 
        the data bits.
    """
    def __init__(self, timeout):
        self.alternative_rows = []
        self.alternative_indices = []
        self.bits = []
        self.attributes = {}
        self.valid = False
        self.timeout = timeout

    def set_data(self, data, first_strip):
        data_length = self.file_header.length - 11 # remove checksum, strip id, seq no, strip type and softw. expan
        if first_strip:
            data_length -= (9 + len(self.file_header.filename))
        self.data = data[0:data_length]

    def calculate_checksum(self, data, length):
        # Source:
        # https://github.com/FozzTexx/Distripitor/blob/master/Barcode.m#L311-L317
        c = 0
        l = parse_length(length) - 1

        if l > len(data):
            return -1

        for i in range(l):
            byte = data[i]
            c = ((c & 0xff) + byte + (c >> 8)) & 0x1ff
        return 0x100 - ((c & 0xff) + (c >> 8))

    def convert_bit_row_to_byte(self, row, header_processed):
        copy = row.copy()
        row_bytes = []

        while copy:
            byte = 0
            bit = 1
            if len(copy) == 4 and not header_processed:
                return row_bytes
            for i in range(8):
                if copy.pop(0):
                    byte |= bit
                bit <<= 1
            row_bytes.append(byte)
        return row_bytes

    def is_header_processed(self, num_zeros, row):
        """
            Vertical synchronization section is processed after
            three 0 bytes.     
        """
        add_last_row = False
        if num_zeros > 0: # transition from header to data starts with three 0x00 bytes
            add_last_row = True
        for byte in row:
            if byte == 0x0:
                num_zeros +=1
            else:
                num_zeros = 0
            if num_zeros == 3:
                return True, add_last_row, num_zeros
        return False, add_last_row, num_zeros

    def extract_data_bits_from_row(self, row, index, header_processed):
        if type(row) is list:
            if header_processed and len(row) > 1:
                self.alternative_rows.append(row)
                self.alternative_indices.append(index)
            row = row[0]
        row = row.strip()
        line_data_raw = row[7:-7]
        return convert_dibit_row_to_bit(line_data_raw)

    def extract_all_data_bits(self, rows):
        """
            Extracts all data bits from all rows
        """
        header_processed = False
        last_row = None
        add_last_row = False
        num_zeros = 0
        for index, row in enumerate(rows):
            if len(row) == 0:
                continue
            line_data = self.extract_data_bits_from_row(row, index, header_processed)

            if header_processed is False:
                line_bytes = self.convert_bit_row_to_byte(line_data, header_processed)
                header_processed, add_last_row, num_zeros = self.is_header_processed(num_zeros, line_bytes)
                if add_last_row == True:
                    self.bits += last_row

            if header_processed is True:
                self.bits += line_data

            last_row = convert_dibit_row_to_bit(row[7:-7])

    def parse_up_to_checksum(self):
        """
            Processes the first data fields up to the checksum field
        """
        if len(self.bits) % 8 != 0:
            self.bits += [0, 0, 0, 0]
        data = self.convert_bit_row_to_byte(self.bits, True)
        num_zeros = 0
        for index, data_byte in enumerate(data):
            if num_zeros == 3:
                data = data[index-3:]
                break
            if data_byte == 0x00:
                num_zeros += 1
            else:
                num_zeros = 0

        self.attributes['data_sync'] = pop_multiple_items(data, 0, 1)[0]
        self.attributes['expansion_bytes'] = pop_multiple_items(data, 0, 2)
        self.attributes['length'] = pop_multiple_items(data, 0, 2)
        self.attributes['checksum'] = pop_multiple_items(data, 0, 1)[0]
        return data

    def parse_file_header(self, data, first_strip):
        """
            Processes all data fields after the checksum field
        """
        self.attributes['strip_id'] = pop_multiple_items(data, 0, 6)
        self.attributes['seq_no'] = pop_multiple_items(data, 0, 1)[0]
        self.attributes['strip_type'] = pop_multiple_items(data, 0, 1)[0]
        self.attributes['software_expansion'] = pop_multiple_items(data, 0, 2)
        if first_strip:
            self.attributes['os_sys_type'] = pop_multiple_items(data, 0, 1)[0]
            self.attributes['num_files'] = pop_multiple_items(data, 0, 1)[0]
            self.attributes['cauzin_type'] = pop_multiple_items(data, 0, 1)[0]
            self.attributes['os_filetype'] = pop_multiple_items(data, 0, 1)[0]
            self.attributes['file_length'] = pop_multiple_items(data, 0, 3)
            self.attributes['filename'] = ''
            while data[0] != 0x00 and data[0] != 0xFF:
                self.attributes['filename'] += chr(pop_multiple_items(data, 0, 1)[0])
            self.attributes['terminator'] = pop_multiple_items(data, 0, 1)[0]
            self.attributes['block_expand'] = pop_multiple_items(data, 0, 1)[0]

        self.file_header = FileHeader(self.attributes, first_strip)
        return data

    def try_alternative_rows(self, raw_data, start_time):
        """
            Try all combinations for rows with multiple solutions
        """
        for element in itertools.product(*self.alternative_rows):
            now = datetime.datetime.now().replace(microsecond=0)
            difference = now - start_time
            if (difference.seconds // 60) > self.timeout:
                self.valid = False
                break
            new_raw_data = raw_data.copy()
            for i, item in enumerate(element):
                new_raw_data[self.alternative_indices[i]] = item
                new_raw_data[self.alternative_indices[i]] = item
            self.bits = []
            self.extract_all_data_bits(new_raw_data)
            data = self.parse_up_to_checksum()
            if self.attributes['checksum'] != self.calculate_checksum(data, self.attributes['length']):
                self.valid = True
                break

    def extract_data(self, raw_data, first_strip=False, start_time=None):
        self.extract_all_data_bits(raw_data)
        data = self.parse_up_to_checksum()

        if self.attributes['checksum'] != self.calculate_checksum(data, self.attributes['length']):
            if len(self.alternative_rows) > 0:
                self.try_alternative_rows(raw_data, start_time)
            else:
                self.valid = False
                print('Invalid checksum!')
        else:
            self.valid = True
        data = self.parse_file_header(data, first_strip)
        self.set_data(data, first_strip)
