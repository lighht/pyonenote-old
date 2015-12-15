class SectionDB:
    sectionDB = []

    def __init__(self, sections_list=None):
        if sections_list is not None:
            self.sectionDB = sections_list

    def fetch(self):
        print('in fetch of sections_db')
