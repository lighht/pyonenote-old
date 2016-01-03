import os
import pickle
import sys

from pyonenote import NOTEBOOK_DB
from pyonenote import SESSION_FILE
from pyonenote.api import client, restapi, notebooks


class NotebookDB:
    notebookDB = []

    def __init__(self, notebooks_list=None):
        if notebooks_list is not None:
            self.notebookDB = notebooks_list

    def write(self):
        with open(NOTEBOOK_DB, 'wb') as output:
            print('Writing notebooks of size ' + str(len(self.notebookDB)))
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def read(self):
        with open(NOTEBOOK_DB, 'rb') as input:
            obj = pickle.load(input)
        self.notebookDB = obj.notebookDB

    def set_notebook_list(self, notebook_list):
        self.notebookDB = notebook_list

    def fetch(self):
        client_obj = client.Client()
        if not os.path.exists(SESSION_FILE):
            print('session file not found')
            sys.exit()
        else:
            session_info = client_obj.get_session_info()
            print('session info loaded')
        rest_api_obj = restapi.RestAPI(session_info)
        notebooks_list_json = rest_api_obj.get_notebooks_list()['value']
        notebooks_list = []
        for i in range(0, len(notebooks_list_json)):
            current_notebook = notebooks.Notebook(data=notebooks_list_json[i])
            notebooks_list.append(current_notebook)
        self.notebookDB = notebooks_list
        self.write()

    def list(self):
        self.read()
        for item in self.notebookDB:
            print(item.name)
