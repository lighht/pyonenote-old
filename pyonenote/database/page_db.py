import os
import pickle
import sys

from pyonenote import PAGE_DB
from pyonenote import SESSION_FILE
from pyonenote.api import client, restapi, pages


class PageDB:
    pageDB = []

    def __init__(self, pages_list=None):
        if pages_list is not None:
            self.pageDB = pages_list

    def write(self):
        with open(PAGE_DB, 'wb') as output:
            print('Writing pages list of size ' + str(len(self.pageDB)))
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def read(self):
        with open(PAGE_DB, 'rb') as input:
            obj = pickle.load(input)
        self.pageDB = obj.pageDB

    def set_pages_list(self, pages_list):
        self.pageDB = pages_list

    def fetch(self):
        client_obj = client.Client()
        if not os.path.exists(SESSION_FILE):
            print('file not found')
            sys.exit()
        else:
            session_info = client_obj.get_session_info()
            print('session info loaded')
        rest_api_obj = restapi.RestAPI(session_info)
        pages_list_json = rest_api_obj.get_pages_list()['value']
        pages_list = []
        for i in range(0, len(pages_list_json)):
            data = pages_list_json[i]
            current_notebook = pages.Page(data=data)
            pages_list.append(current_notebook)
        self.pageDB = pages_list
        self.write()

    def push(self, filename=None):
        if filename is not None:
            client_obj = client.Client()
            if not os.path.exists(SESSION_FILE):
                print('file not found')
                sys.exit()
            else:
                session_info = client_obj.get_session_info()
                print('session info loaded')
            rest_api_obj = restapi.RestAPI(session_info)
            rest_api_obj.push_page_to_default_notebook(filename=filename)
        else:
            print('file name none')

    def list(self, filename):
        self.read()
        for item in self.pageDB:
            print(item.title)
