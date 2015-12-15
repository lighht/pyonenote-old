class Notebook:
    def __init__(self, data):
        self.is_default = data.get('isDefault')
        self.is_shared = data.get('isShared')
        self.notebook_id = data.get('id')
        self.name = data.get('name')
        self.created_by = data.get('createdBy')
        self.created_time = data.get('createdTime')
        self.sections = []

    def set_sections(self, section_list):
        self.sections = section_list
