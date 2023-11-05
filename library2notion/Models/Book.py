
class Book:
    def __init__(self, fileName, format, title = '', author = '', publisher = '', isbn = '', notion_page_id = None):
        self.fileName = fileName
        self.title = title
        self.priority = ''
        tags = (fileName + format).split('/')[:-1][1:]
        self.tags = tags
        self.status = ''
        self.author = author
        self.publisher = publisher
        self.comments = ''
        self.format = format
        self.isbn = isbn
        self.ignore = False
        self.notion_page_id = notion_page_id

    def extractMetadata(self):
        pass