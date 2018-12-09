OS = {
    0x00:	'Cauzin generic strip format',
    0x01:	'COLOS',
    0x10:	'Apple DOS 3.3',
    0x11:	'Apple ProDOS',
    0x12:	'Apple CP/M 2.0',
    0x14:	'PC/MS-DOS (2.1)',
    0x15:	'Macintosh MacBinary',
    0x20:	'Reserved - PC/MS-DOS'
}

CAUZIN_FILE_TYPE = {
    0x00:	"Other / Unknown / Don't care",
    0x01:	'Text file',
    0x02:	'Binary executable or object code',
    0x04:	'Tokenized BASIC',
    0x10:	'Compressed with proprietary cauzin algorithm',   
}

OS_FILE_TYPE = {
    # Apple DOS 3.3
    0x10: {
        0x00:	'Text file',
        0x01:	'Integer BASIC file',
        0x02:	'Applesoft BASIC file',
        0x04:	'Binary file',
        0x10:	'Relocatable object module file',
        0x20:	"'A' type file, unsupported",
        0x40:	"'B' type file, unsupported",
    },
    # Apple ProDOS
    0x11: {
        0x04:	'ASCII text file',
        0x06:	'Binary file',
        0xfa:	'Integer BASIC file',
        0xfc:	'Applesoft BASIC file',
        0xfe:	'Relocatable object module file',
        0xff:	'System file',
    },
    # IBM PC-DOS/MS-DOS
    0x14: {
        0x00:	'Executable DOS file',
        0x01:	'Other DOS file',
    },
    # Macintosh
    0x15: {
        0x00:	'MacBinary',
        0x01:	'Data fork, non-MacBinary',
    }
}