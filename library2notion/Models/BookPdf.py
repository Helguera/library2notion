
from library2notion.Models.Book import Book
from PyPDF2 import PdfReader

class BookPdf(Book):

    def __init__(self, fileName, format):
        super().__init__(fileName, format)

    def extractMetadata(self):
        filePath = self.fileName + '.' + self.format.lower()
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

        return super().extractMetadata()