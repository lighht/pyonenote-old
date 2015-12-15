class Section:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.created_by = data.get('createdBy')
        self.created_time = data.get('createdTime')
