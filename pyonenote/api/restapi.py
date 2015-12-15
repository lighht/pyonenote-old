import sys

import requests


class RestAPI:
    def __init__(self, session_info):
        self.session_info = session_info

    def get_pages_list(self):
        bearer_token = 'Bearer ' + self.session_info['access_token']
        headers = {
            'Authorization': bearer_token
        }

        parameters = {
            'orderBy': 'createdTime',
            'top': '100',
            'count': 'true',
            'expand': 'parentNotebook, parentSection',
            'pageLevel': 'true'
        }

        try:
            response = requests.get("https://www.onenote.com/api/v1.0/me/notes/pages", params=parameters,
                                    headers=headers)
            pages_info = response.json()
        except:
            print('request failed')
            sys.exit(1)

        return pages_info

    def get_notebooks_list(self):
        bearer_token = 'Bearer ' + self.session_info['access_token']
        headers = {
            'Authorization': bearer_token
        }
        try:
            response = requests.get("https://www.onenote.com/api/v1.0/me/notes/notebooks", headers=headers)
            notebook_list = response.json()
        except:
            print('request  for notebooks failed\n')
            sys.exit(0)
        return notebook_list

    def get_sections_in_notebook(self, notebook_id):
        bearer_token = 'Bearer ' + self.session_info['access_token']
        request_url = 'https://www.onenote.com/api/v1.0/me/notes/notebooks/' + str(notebook_id) + '/sections'
        headers = {
            'Authorization': bearer_token
        }
        try:
            response = requests.get(request_url, headers=headers)
            section_list = response.json()
        except:
            sys.exit(0)
        return section_list

    def push_page_to_default_notebook(self, filename=None):
        bearer_token = 'Bearer ' + self.session_info['access_token']
        request_url = 'https://www.onenote.com/api/v1.0/me/notes/pages/'
        headers = {
            'Content-Type': 'application/xhtml+xml',
            'Authorization': bearer_token
        }
        data = self.text_to_html(filename)
        try:
            response = requests.post(request_url, data=data, headers=headers)
            if response.ok:
                print('Push success')
        except:
            print('push failed')

    def text_to_html(self, filename=None):

        head = """
            <?xml version="1.0" encoding="utf-8" ?>
            <html xmlns="http://www.w3.org/1999/xhtml" lang="en-us">
                <head>
                    <title>
                    """
        filename_list = filename.split("/")
        title = filename_list[len(filename_list) - 1]
        titlend = """
                    </title>
                    <meta name="created" content="2014-03-17T09:00:00-08:00" />
                </head>
                <body>
                    <p>
                    """
        with open(filename, 'r') as input_file:
            body = input_file.read()
        bodyend = """</p>
                </body>
            </html>
            """
        return (head + title + titlend + body + bodyend)
