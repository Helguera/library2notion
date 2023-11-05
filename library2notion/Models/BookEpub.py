
from library2notion.Models.Book import Book
import epub_meta

class BookEpub(Book):

    def __init__(self, fileName, format):
        super().__init__(fileName, format)

    def extractMetadata(self):
        filePath = self.fileName + '.' + self.format.lower()
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

        return super().extractMetadata()