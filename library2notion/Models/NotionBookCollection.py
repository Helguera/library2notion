from library2notion.ProgressBar import printProgressBar
from library2notion.Models.BookCollection import BookCollection
from library2notion.Models.Book import Book

class NotionBooksCollection(BookCollection):
    def __init__(self, notionIntegration):
        super().__init__(notionIntegration)

    def fetchAllBooks(self):
        printProgressBar(0, 100, prefix = '➖ Getting books from Notion:', suffix = 'Complete', length = 100)
        rawResponse = self.notionIntegration.findPagesInDatabase()
        try:
            formats = [x["name"] for x in item["properties"]["Format"]["multi_select"]]
        except:
            formats = ['PAPER']
        for index, item in enumerate(rawResponse):
            for format in formats:
                try:
                    file_name = item["properties"]["File Name"]["title"][0]["plain_text"]
                except (KeyError, IndexError):
                    continue #It has to exist

                try:
                    title = item["properties"]["Title"]["rich_text"][0]["plain_text"]
                except (KeyError, IndexError):
                    title = ''

                try:
                    author = item["properties"]["Author"]["rich_text"][0]["plain_text"]
                except (KeyError, IndexError):
                    author = ''

                try:
                    publisher = item["properties"]["Publisher"]["rich_text"][0]["plain_text"]
                except (KeyError, IndexError):
                    publisher = ''

                try:
                    isbn = item["properties"]["ISBN"]["rich_text"][0]["plain_text"]
                except (KeyError, IndexError):
                    isbn = ''

                temp_book = Book(
                    fileName=file_name,
                    format=format,
                    title=title,
                    author=author,
                    publisher=publisher,
                    isbn=isbn,
                    notion_page_id=item["id"]
                )
                self.bookCollection.append(temp_book)
            printProgressBar(index + 1, len(rawResponse), prefix = '{} Getting books from Notion ({}/{}):'.format("✅" if index+1 == len(rawResponse) else "➖", index+1, len(rawResponse)), suffix = 'Complete', length = 100)
