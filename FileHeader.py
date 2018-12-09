from DataFieldHelper import * 

class FileHeader:
    def __init__(self, attributes, first_strip):
        self.first_strip = first_strip
        if self.first_strip:
            self.parse_fields_first_strip(attributes)
        self.parse_base_fields(attributes)
    
    def parse_fields_first_strip(self, attributes):
        self.os_type = parse_os_type(attributes['os_sys_type'])
        self.num_files = attributes['num_files']
        self.cauzin_filetype = parse_cauzin_filetype(attributes['cauzin_type'])
        self.os_filetype = parse_os_filetype(attributes['os_sys_type'], attributes['os_filetype'])
        self.file_length = parse_length(attributes['file_length'])
        self.filename = attributes['filename']

    def parse_base_fields(self, attributes):
        self.length = parse_length(attributes['length'])
        self.strip_id = parse_strip_id(attributes['strip_id'])
        self.seq_num = attributes['seq_no']
        self.strip_type = parse_strip_type(attributes['strip_type'])
        
    def __str__(self):
        output = 'Strip id: ' + str(self.strip_id) + \
            '\n Sequence number: ' + str(self.seq_num) + \
            '\n Strip type: ' + self.strip_type + \
            '\n Length: ' + str(self.length) 
        if self.first_strip:
            output += '\n Filename: ' + self.filename + \
                '\n Os type: ' + self.os_type + \
                '\n Number of files: ' + str(self.num_files) + \
                '\n Cauzin file type: ' + self.cauzin_filetype + \
                '\n Os file type: ' + self.os_filetype + \
                '\n File length: ' + str(self.file_length)
        return output