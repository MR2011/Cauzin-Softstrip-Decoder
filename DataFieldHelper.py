from CauzinFileConstants import *


def parse_length(length_bytes):
    shift = 8 * (len(length_bytes) - 1)
    length = 0
    for byte in reversed(length_bytes):
        length |= (byte << shift)
        shift -= 8
    return length


def parse_strip_type(strip_type):
    if strip_type == 0x00:
        return 'Standard Softstrip data strip'
    elif strip_type == 0x01:
        return 'Special key strip (undefined)'
    elif strip_type >= 0x02 and strip_type <= 0xff:
        return 'Other formats (undefined)'
    else:
        return 'Invalid strip type: ' + hex(strip_type)


def parse_os_type(os):
    if os in OS:
        return OS[os]
    else:
        return 'Invalid OS type: ' + hex(os)


def parse_strip_id(strip_id_bytes):
    strip_id = ''
    for byte in strip_id_bytes:
        strip_id += chr(byte)
    return strip_id


def parse_cauzin_filetype(filetype):
    if filetype in CAUZIN_FILE_TYPE:
        return CAUZIN_FILE_TYPE[filetype]
    else:
        return 'Invalid cauzin file type: ' + hex(filetype)


def parse_os_filetype(os, filetype):
    if os == 0x00 or os == 0x01:
        return 'Unknown'
    elif os in OS_FILE_TYPE:
        if filetype in OS_FILE_TYPE[os]:
            return OS_FILE_TYPE[os][filetype]
        else:
            return 'Invalid OS file type: ' + hex(filetype)
    else:
        return 'Invalid OS type: ' + hex(os)
