
from .ProgressBar import printProgressBar

class BookCollection:
    def __init__(self):
        self.bookCollection = []

    def insert(self, book): 
        if not self.existsByFileName(book.fileName):
            self.bookCollection.append(book)
        else:
            duplicated = next(x for x in self.bookCollection if x.fileName == book.fileName)
            duplicated.formats.append(book.temp_format.upper().replace('.', ''))


    def existsByFileName(self, fileName):
        if len([x for x in self.bookCollection if x.fileName == fileName]) != 0:
            return True
        return False

    def copyAllToExcel(self, ws):
        rowNum = 2
        length = len(self.bookCollection)
        printProgressBar(0, length-1, prefix = 'Generating .xlsx file:', suffix = 'Complete', length = 100)
        for index, book in enumerate(self.bookCollection):
            printProgressBar(index, length-1, prefix = 'Generating .xlsx file: ', suffix = 'Complete', length = 100)
            if book.action in ['update', 'upload']:
                book.copyToExcel(rowNum, ws)
                rowNum += 1

    def printAll(self):
        for book in self.bookCollection:
            print(book.fileName + ' - ' + str(book.formats))

    def createJson(self):
        mylist = []
        for book in self.bookCollection:
            mylist.append({'filename': book.fileName, 'action': book.action, 'formats': book.formats})
        return mylist

    def findBook(self, fileName,):
        listBooks = [x for x in self.bookCollection if x.fileName == fileName]
        if len(listBooks) != 0:
            return listBooks[0]
        return None

    def removeBook(self, book):
        self.bookCollection.remove(book)

    def isEmpty(self):
        for book in self.bookCollection:
            if book.action in ['upload', 'update']:
                return False
        return True

    def extractMetadataFromBooks(self, forceUpload):
        length = len(self.bookCollection)
        printProgressBar(0, length, prefix = 'Extracting metadata:   ', suffix = 'Complete', length = 100)
        for index, book in enumerate(self.bookCollection):
            if (book.action in ['update', 'upload']) or forceUpload:
                book.extractMetadata()
            printProgressBar(index+1, length, prefix = 'Extracting metadata:   ', suffix = 'Complete', length = 100)
