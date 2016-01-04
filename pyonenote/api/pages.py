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


from PyQt5.QtCore import (pyqtSignal, QThread, QMutex, QWaitCondition, QMutexLocker)


class FetchPage(QThread):
    fetchSignal = pyqtSignal(str, name='fetchComplete')

    def __init__(self, parent=None):
        super(FetchPage, self).__init__(parent)
        print('thread initialized')
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        self.restart = False
        self.abort = False

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait()

    def fetch(self, page):
        locker = QMutexLocker(self.mutex)
        self.page = page
        if page.content is not None:
            print('Returning old content')
            self.fetchSignal.emit(page.content)
        else:
            if not self.isRunning():
                self.start(QThread.LowPriority)
            else:
                self.restart = True
                self.condition.wakeOne()

    def run(self):
        print("running page fetch")
        rest_api = RestAPI()
        self.page.content = (rest_api.get_page_content(self.page.content_url))
        # print(self.page.content)
        self.fetchSignal.emit(self.page.content)
        # self.fetchSignal.emit()
        print('signal emitted')
        self.mutex.lock()
        if not self.restart:
            self.condition.wait(self.mutex)
        self.restart = False
        self.mutex.unlock()
