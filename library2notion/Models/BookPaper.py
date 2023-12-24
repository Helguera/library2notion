
from library2notion.Models.Book import Book
import json

class BookPaper(Book):

    def __init__(self, fileName, format):
        super().__init__(fileName, format)

    def extractMetadata(self):
        filePath = self.fileName + '.' + self.format.lower()
            
        f = open(filePath)
        data = json.load(f)
        try:
            self.title = data['Title']
            self.author = data['Author']
            self.publisher = data['Publisher']
            self.isbn = data['ISBN']
        except Exception as e:
            pass

        return super().extractMetadata()