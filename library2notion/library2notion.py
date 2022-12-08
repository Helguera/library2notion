
import epub_meta
import openpyxl
import os
import pandas as pd
from PyPDF2 import PdfReader
import json
import collections
import argparse
import csv2notion

# LINE ARGUMENTS ------------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-p", "--Path", help="Origin path", required=True)
parser.add_argument("-l", "--LogFilePath", help="Log File path", required=False)
parser.add_argument("-e", "--Extensions", nargs='+', help="Supported Extensions", required=False)

parser.add_argument("-t", "--NotionToken", help="Notion Token", required=False)
parser.add_argument("-u", "--NotionDbUrl", help="Notion DB URL", required=False)
parser.add_argument("-f", "--ForceUpload", help="Force upload to Notion", required=False, action='store_true')

args = parser.parse_args()

if args.Path: path = args.Path
if args.LogFilePath: logFilePath = args.LogFilePath
if args.Extensions: 
    supported_extensions = args.Extensions
else:
    supported_extensions = ['.epub', '.pdf']
if args.NotionToken: notionToken = args.NotionToken
if args.NotionDbUrl: notionDbUrl = args.NotionDbUrl
forceUpload = False
if args.ForceUpload: forceUpload = True


# ---------------------------------------------------------------------------------------

wb = openpyxl.Workbook() 
ws1 = wb.active
ws1.title = "books"

ws1.cell(row=1, column=1).value = 'File Name'
ws1.cell(row=1, column=2).value = 'Title'
ws1.cell(row=1, column=3).value = 'Priority'
ws1.cell(row=1, column=4).value = 'Tags'
ws1.cell(row=1, column=5).value = 'Status'
ws1.cell(row=1, column=6).value = 'Author'
ws1.cell(row=1, column=7).value = 'Publisher'
ws1.cell(row=1, column=8).value = 'Comments'
ws1.cell(row=1, column=9).value = 'Format'
ws1.cell(row=1, column=10).value = 'ISBN'

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

    def copyAllToExcel(self):
        rowNum = 2
        length = len(self.bookCollection)
        printProgressBar(0, length-1, prefix = 'Generating .xlsx file:', suffix = 'Complete', length = 100)
        for index, book in enumerate(self.bookCollection):
            printProgressBar(index, length-1, prefix = 'Generating .xlsx file: ', suffix = 'Complete', length = 100)
            if book.action in ['update', 'upload']:
                book.copyToExcel(rowNum)
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

    def extractMetadataFromBooks(self):
        length = len(self.bookCollection)
        printProgressBar(0, length, prefix = 'Extracting metadata:   ', suffix = 'Complete', length = 100)
        for index, book in enumerate(self.bookCollection):
            if (book.action in ['update', 'upload']) or forceUpload:
                book.extractMetadata()
            printProgressBar(index+1, length, prefix = 'Extracting metadata:   ', suffix = 'Complete', length = 100)

class Book:
    def __init__(self, fileName, formats, temp_format):
        self.fileName = fileName
        self.title = ''
        self.priority = ''
        tags = (fileName + temp_format).split('/')[:-1]
        self.tags = tags
        self.status = ''
        self.author = ''
        self.publisher = ''
        self.comments = ''
        self.formats = formats
        self.temp_format = temp_format
        self.isbn = ''
        self.action = 'upload'

    def copyToExcel(self, rowNum):
        ws1.cell(row=rowNum, column=1).value = self.fileName
        ws1.cell(row=rowNum, column=2).value = self.title    
        ws1.cell(row=rowNum, column=3).value = self.priority
        ws1.cell(row=rowNum, column=4).value = self.tags
        ws1.cell(row=rowNum, column=5).value = self.status
        ws1.cell(row=rowNum, column=6).value = self.author
        ws1.cell(row=rowNum, column=7).value = self.publisher
        ws1.cell(row=rowNum, column=8).value = self.comments
        ws1.cell(row=rowNum, column=9).value = ', '.join(self.formats)
        ws1.cell(row=rowNum, column=10).value = self.isbn

    def extractMetadata(self):
        for format in self.formats:
            filePath = self.fileName + '.' + format.lower()

            if 'EPUB' in format.upper():
                data = epub_meta.get_epub_metadata(filePath, read_cover_image=True, read_toc=True)

                # TITLE
                self.title = data.title

                # AUTHOR
                self.author = ' '.join(data.authors)

                # PUBLISHER
                if data.publisher:
                    self.publisher = data.publisher.replace(',','')

                # ISBN
                self.isbn = ' '.join(data.identifiers)

            elif 'PDF' in format.upper():
                try:
                    reader = PdfReader(filePath)
                    pdf_info = reader.metadata

                    # TITLE
                    if pdf_info.title: 
                        self.title = pdf_info.title
                    else:
                         self.title = filePath.split('/')[len(filePath.split('/')) - 1].split('.')[0]

                    # AUTHOR
                    author = ''
                    if pdf_info.author is not None:
                        self.author = pdf_info.author

                except Exception as e:
                    if str(e) != 'EOF marker not found':
                        self.status = 'BROKEN!'

            if self.tags[len(self.tags) - 1] == self.title:
                self.tags = self.tags[:-1]
            self.tags = ', '.join(self.tags[1:])

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if iteration == 0 and total == 0:
        bar = fill*100
        print(f'\r{prefix} |{bar}| 100.0% {suffix}', end = printEnd)
        return
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#####################################################################################################################

files_path = [os.path.abspath(os.path.join(path, x)) for x in os.listdir(path)]
files = []
temp_files = []

for r, d, f in os.walk(path):
    for file in f:
        if filter(lambda element: file in element, supported_extensions):
            files.append(os.path.join(r, file))
temp_files = files.copy()
temp_files = filter(lambda x: '._' not in x, files)
files = filter(lambda x: '._' not in x, files)

bookCollection = BookCollection()

total_files = 0
for index, my_file in enumerate(temp_files, start=1):
    total_files += 1

print('\nTOTAL FILES: ' + str(total_files) + '\n')
printProgressBar(0, total_files, prefix = 'Detecting files:       ', suffix = 'Complete', length = 100)

for index, my_file in enumerate(files, start=1):

    if os.path.splitext(my_file)[1] in supported_extensions:
        book = Book(os.path.splitext(my_file)[0], [os.path.splitext(my_file)[1].replace('.','').upper()], os.path.splitext(my_file)[1])
        bookCollection.insert(book)

    printProgressBar(index, total_files, prefix = 'Detecting files:       ', suffix = 'Complete', length = 100)

# JSON PROCESSING
deleted = []
if ('logFilePath' in locals() and os.path.exists(os.path.join(logFilePath, 'log.json')) and not forceUpload):
    with open(os.path.join(logFilePath, 'log.json'), 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
        printProgressBar(0, len(json_object)-1, prefix = 'Analazing log file:    ', suffix = 'Complete', length = 100)
        for index, value in enumerate(json_object):
            bookInCollection = bookCollection.findBook(value['filename'])
            if bookInCollection is not None:
                if collections.Counter(bookInCollection.formats) == collections.Counter(value['formats']):
                    bookInCollection.action = "do nothing"
                else:
                    json_object[index]['formats']= bookInCollection.formats
                    bookInCollection.action = "update"
            else:
                json_object[index]['action']= 'DELETED'
                deleted.append(json_object[index])
            printProgressBar(index, len(json_object)-1, prefix = 'Analazing log file:    ', suffix = 'Complete', length = 100)

    deleted_json_object = json.dumps(deleted, indent=2)
    with open("deleted.json", "w") as outfile:
        outfile.write(deleted_json_object)

json_object = json.dumps(bookCollection.createJson(), indent=2)
with open(os.path.join(logFilePath, 'log.json'), "w") as outfile:
    outfile.write(json_object)

# bookCollection.printAll()
bookCollection.extractMetadataFromBooks()
bookCollection.copyAllToExcel()
wb.save(filename='books.xlsx')
df = pd.read_excel('books.xlsx', 'books', index_col=None)
df.to_csv ('books.csv', index = None, header=True, encoding='utf-8-sig')
printProgressBar(0, 0, prefix = 'Converting to .csv:    ', suffix = 'Complete', length = 100)

if not bookCollection.isEmpty() or forceUpload:
    if 'notionToken' in locals() and 'notionDbUrl' in locals():
        print('\n')
        command = 'csv2notion --token ' + notionToken + ' --url ' + notionDbUrl + ' --merge books.csv --merge-only-column "File Name" --merge-only-column "Title" --merge-only-column "Author" --merge-only-column "Publisher" --merge-only-column "Format" --merge-only-column "Tags" --merge-only-column "ISBN" --column-types "text, select, multi_select, select, text, text, text, multi_select, text" --add-missing-columns --verbose'
        os.system(command)
    else:
        print('\n\nCSV file has been created but no csv2notion script was provided.')
else:
    print('\n\nEverything up to date. Nothing to upload to Notion.')

print('\nDONE.')