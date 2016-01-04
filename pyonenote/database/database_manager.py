import pickle

from pyonenote import PAGE_DB
from pyonenote.api import restapi, pages


class Dbm:
    notebook_list = []
    pages_list = []

    def __init__(self, notebooks_list=None):
        if notebooks_list is not None:
            self.notebook_list = notebooks_list
            self.pages_list_json = ''
        self.notebook_dict = {}
        self.section_dict = {}
        self.pages_dict = {}
        self.hierarchy_dict = {}
        self.dataset = [self.hierarchy_dict, self.notebook_dict, self.section_dict, self.pages_dict]

    def write(self, dataset=None):
        if dataset is None:
            dataset = self.dataset
        print('Writing')
        print(dataset)
        with open(PAGE_DB, 'wb') as output:
            pickle.dump(dataset, output, pickle.HIGHEST_PROTOCOL)

    # Reads the object which was written as JSON during fetch
    # Creates notebook, section and page dictionaries with {id:object} format
    # Creates a hierarchy dictionary with
    # {notebook_id1:[
    #   section_id1:[page_id_1, page_id2...],
    #   section_id2:[page_id_1, page_id2...], ..]
    #  notebook_id2:[.[], ..] }
    def read(self):
        with open(PAGE_DB, 'rb') as input:
            obj = pickle.load(input)
        self.dataset = obj
        [self.hierarchy_dict, self.notebook_dict, self.section_dict, self.pages_dict] = self.dataset
        # for notebook in self.hierarchy_dict.keys():
        #     print(self.notebook_dict[notebook].name)
        #     for section in self.hierarchy_dict[notebook].keys():
        #         print("--"+self.section_dict[section].name)
        #         for page in self.hierarchy_dict[notebook][section]:
        #             print("  --"+self.pages_dict[page].title)

    def get_hierarchy_dict(self):
        return [self.hierarchy_dict, self.notebook_dict, self.section_dict, self.pages_dict]

    def get_notebook_list(self):
        return self.notebook_list

    def get_pages_list(self):
        return self.pages_list

    def fetch(self):
        rest_api_obj = restapi.RestAPI()
        response = rest_api_obj.get_pages_list()
        self.pages_list_json = response['value']
        pages_list = []

        for i in range(0, len(self.pages_list_json)):
            data = self.pages_list_json[i]
            current_page = pages.Page(data=data)
            self.pages_dict[current_page.id] = current_page
            current_notebook_id = current_page.parent_notebook.notebook_id
            current_section_id = current_page.parent_section.id

            if current_notebook_id not in self.notebook_dict.keys():
                self.notebook_dict[current_notebook_id] = current_page.parent_notebook
                self.section_dict[current_section_id] = current_page.parent_section
                self.hierarchy_dict[current_notebook_id] = {}
                self.hierarchy_dict[current_notebook_id][current_section_id] = [current_page.id]
            elif current_section_id not in self.section_dict.keys():
                self.section_dict[current_section_id] = current_page.parent_section
                self.hierarchy_dict[current_notebook_id][current_section_id] = [current_page.id]
            else:
                self.hierarchy_dict[current_notebook_id][current_section_id].append(current_page.id)
            pages_list.append(current_page)
        self.write()
