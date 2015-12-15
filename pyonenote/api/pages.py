from pyonenote.api.notebooks import Notebook
from pyonenote.api.sections import Section


class Page:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.last_modified_time = data.get('lastModifiedTime')
        self.created_time = data.get('createdTime')
        self.content_url = data.get('contentUrl')
        self.parent_notebook = Notebook(data=data.get('parentNotebook'))
        self.parent_section = Section(data=data.get('parentSection'))
