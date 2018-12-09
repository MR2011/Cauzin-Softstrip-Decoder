class RowComponents:
    """
        Collects information about all pixel lines which are necessary
        for the header processing.
    """
    def __init__(self, pixel_matrix):
        self.components = []
        self.all_min_sizes = []
        self.all_max_sizes = []
        self.all_avg_sizes = []
        self.all_counts = []
        self.last_element_sizes = []
        self.process_pixel_matrix(pixel_matrix)

    def process_pixel_matrix(self, pixel_matrix):
        last_component = {'index': -1, 'value': -1, 'size': 0}
        for index, row in enumerate(pixel_matrix):
            self.process_row(row, last_component, index)
            last_component = {'value': -1, 'size': 0}
        self.normalize_meta_info()

    def normalize_meta_info(self):
        max_max_size = max(self.all_max_sizes)
        min_max_size = min(self.all_max_sizes)
        max_min_size = max(self.all_min_sizes)
        min_min_size = min(self.all_min_sizes)
        max_avg_size = max(self.all_avg_sizes)
        min_avg_size = min(self.all_avg_sizes)
        max_count = max(self.all_counts)
        min_count = min(self.all_counts)
        for row in self.components:
            row['max_size'] = (row['max_size'] - min_max_size) / float((max_max_size - min_max_size))
            row['min_size'] = (row['min_size'] - min_min_size) / float((max_min_size - min_min_size))
            row['avg_size'] = (row['avg_size'] - min_avg_size) / float((max_avg_size - min_avg_size))
            row['count'] = (row['count'] - min_count) / float((max_count - min_count))

    def remove_overhead(self, row_components, components_count):
        if row_components[0]['value'] == 0:
            del row_components[0]
            components_count -= 1
        if len(row_components) > 1 and row_components[0]['value'] == 0:
            del row_components[-1]
            components_count -= 1
        return row_components, components_count

    def process_row(self, row, component, index):
        components_count = 0
        row_components = []
        min_size = len(row)
        max_size = 0
        for item in row:
            if item == component['value']:
                component['size'] += 1
            elif component['value'] == -1:
                component['value'] = item
                component['size'] = 1
            else:
                if component['size'] < min_size:
                    min_size = component['size']
                if component['size'] > max_size:
                    max_size = component['size']
                components_count += 1
                row_components.append(component)
                component = {'index': index,'value': item, 'size': 1}
        components_count += 1
        if components_count > 1:
                row_components, components_count = self.remove_overhead(row_components, components_count)
                self.all_min_sizes.append(min_size)
                self.all_max_sizes.append(max_size)
                self.all_counts.append(components_count)
                self.all_avg_sizes.append(len(row)/float(components_count))
                self.last_element_sizes.append(row_components[-1]['size'])
                self.components.append({'max_size': max_size, 'min_size': min_size, 'avg_size': len(row)/float(components_count), 'count': components_count,'components': row_components})
