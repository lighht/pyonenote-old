from pyonenote.api.notebooks import Notebook
from pyonenote.api.restapi import RestAPI
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
        self.content = None

    def setContent(self, content):
        self.content = content

    # Use this method to not return None
    def getContent(self):
        if self.content is None:
            rest_api = RestAPI()
            self.content = (rest_api.get_page_content(self.content_url))
        return self.content
