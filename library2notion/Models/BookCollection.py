import sys
sys.path.append(".")
from library2notion.ProgressBar import printProgressBar
import time

class BookCollection:
    def __init__(self, notionIntegration):
        self.bookCollection = []
        self.notionIntegration = notionIntegration

    def insert(self, book):
        if not self.existsFilenameFormat(book.fileName, book.format):
            self.bookCollection.append(book)

    def existsFilenameFormat(self, fileName, format):
        if len([x for x in self.bookCollection if x.fileName == fileName and x.format == format]) != 0:
            return True
        return False

    def existsByFileName(self, fileName):
        if len([x for x in self.bookCollection if x.fileName == fileName]) != 0:
            return True
        return False

    def printAll(self):
        for book in self.bookCollection:
            print("{} - {} - {}".format(book.fileName, book.format, book.tags))

    def findBook(self, fileName):
        listBooks = [x for x in self.bookCollection if x.fileName == fileName]
        if len(listBooks) != 0:
            return listBooks
        return None

    def removeBook(self, book):
        self.bookCollection.remove(book)

    def isEmpty(self):
        for book in self.bookCollection:
            if book.action in ['upload', 'update']:
                return False
        return True

    def extractMetadataFromBooks(self):
        length = len(self.bookCollection)
        printProgressBar(0, length, prefix = '➖ Extracting metadata:   ', suffix = 'Complete', length = 100)
        for index, book in enumerate(self.bookCollection):
            book.extractMetadata()
            printProgressBar(index+1, length, prefix = '{} Extracting metadata ({}/{}):      '.format("✅" if index+1 == length else "➖", index+1, length), suffix = 'Complete', length = 100)

    def getLength(self):
        return len(self.bookCollection)
    
    def getAll(self):
        return self.bookCollection

