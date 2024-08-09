
import os
import argparse
import logging
import datetime
import sys
import importlib.metadata
import json

from library2notion.Models.BookEpub import BookEpub
from library2notion.Models.BookPdf import BookPdf
from library2notion.Models.BookPaper import BookPaper
from library2notion.ProgressBar import printProgressBar
from library2notion.Models.BookCollection import BookCollection
from library2notion.NotionIntegration import NotionIntegration
from library2notion.Models.NotionBookCollection import NotionBooksCollection


# LINE ARGUMENTS ------------------------------------------------------------------------

def main():

    def validate_args(args):
        if (not args.Path or not args.NotionToken or not args.NotionDbId) and not args.Config:
            print("Error: --Path(-p), --NotionToken(-t), y --NotionDbId(-d) are required when --Config(-c) is not provided")
            sys.exit(1)

    def validate_config_file(args):
        try:
            f = open(args.Config)
        except:
            print("Error: config file not found")
            sys.exit(1)

        try:
            data = json.load(f)
            args.NotionToken = data['notion_secret_token']
            args.NotionDbId = data['notion_db_id']
            args.Path = data['path']
            args.Ignore = data['ignore']
        except:
            print("Error: format of config file is not correct")
            sys.exit(1)

    def create_config_file(args):
        params = {
            'notion_secret_token': args.NotionToken,
            'notion_db_id': args.NotionDbId,
            'path': args.Path,
            'ignore': args.Ignore
        }

        with open('config_l2n.json', 'w') as json_file:
            json.dump(params, json_file, indent=4)

        
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--version", action="version", version = importlib.metadata.version('library2notion'))
    parser.add_argument("-p", "--Path", help="Origin path", required=False)
    parser.add_argument("-t", "--NotionToken", help="Notion Token", required=False)
    parser.add_argument("-d", "--NotionDbId", help="Notion DB ID", required=False)
    parser.add_argument("-f", "--Formats", nargs='+', help="Supported Formats", required=False)
    parser.add_argument("-c", "--Config", help="Config file in JSON format")
    parser.add_argument("-i", "--Ignore", nargs='+', help="Folders to ignore", required=False, default=[])

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--only_new", required=False, action="store_true", default=False, help="Only look for new books")
    group.add_argument("--only_updated", required=False, action="store_true", default=False, help="Only look for updated books")
    group.add_argument("--only_deleted", required=False, action="store_true", default=False, help="Only look for deleted book")

    args = parser.parse_args()

    print('\nlibrary2notion v{} created by Javier Helguera (github.com/helguera) © 2023 MIT License\n'.format(importlib.metadata.version('library2notion')))

    validate_args(args)
    if args.Config:
        validate_config_file(args)
    else:
        create_config_file_answer = input("Do you want to create a config file with provided params for next executions? (Y/n): ")
        print("\n")
        if create_config_file_answer == 'Y':
            create_config_file(args)

    if args.Path: path = args.Path
    base_supported_formats = ['EPUB', 'PDF', 'PAPER']
    if args.Formats:
        supported_formats = list(set([x.upper() for x in args.Formats]).intersection(set(base_supported_formats)))
    else:
        supported_formats = base_supported_formats
    if args.NotionToken: notionToken = args.NotionToken
    if args.NotionDbId: notionDbId = args.NotionDbId
    ignore_dirs = [os.path.normpath(os.path.join(path, ig)) for ig in args.Ignore] if args.Ignore else []

    exec_all = False
    if not args.only_new and not args.only_updated and not args.only_deleted:
        exec_all = True

    # ---------------------------------------------------------------------------------------


    #####################################################################################################################

    def get_logger(logs_path = None, print_msgs = False):
        my_logger = logging.getLogger("library2notion")
        my_logger.setLevel(logging.INFO)
        my_logger.propagate = print_msgs
        if logs_path is None:
            logs_path = os.path.expanduser("./library2notion-logs")  
        os.makedirs(logs_path, exist_ok=True)
        log_file = "{}-{}.log".format("library2notion", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        handler = logging.FileHandler(os.path.join(logs_path, log_file))
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        my_logger.addHandler(handler)
        return my_logger, logs_path, log_file

    files = []
    temp_files = []

    for r, d, f in os.walk(path):
        d[:] = [dir for dir in d if os.path.normpath(os.path.join(r, dir)) not in ignore_dirs]
        for file in f:
            if filter(lambda element: file in element, supported_formats):
                files.append(os.path.join(r, file))
    temp_files = files.copy()
    temp_files = filter(lambda x: '._' not in x, files)
    files = filter(lambda x: '._' not in x, files)

    my_logger, logs_path, logs_file = get_logger()
    my_logger.info("STARTED")
    my_logger.info("Args -> {}".format(args))
    notionIntegration = NotionIntegration(notionToken, notionDbId)
    localBookCollection = BookCollection(notionIntegration)
    notionBookCollection = NotionBooksCollection(notionIntegration)

    total_files = 0
    for index, my_file in enumerate(temp_files, start=1):
        total_files += 1

    printProgressBar(0, total_files, prefix = '➖ Detecting local files:', suffix = 'Complete', length = 100)

    for index, my_file in enumerate(files):
        format = os.path.splitext(my_file)[1].upper()[1:]
        if format in supported_formats:
            book = None
            if format == 'EPUB':
                book = BookEpub(os.path.splitext(my_file)[0], format)
            elif format == 'PDF':
                book = BookPdf(os.path.splitext(my_file)[0], format)
            elif format == 'PAPER':
                book = BookPaper(os.path.splitext(my_file)[0], format)
            if book:
                localBookCollection.insert(book)

        printProgressBar(index + 1, total_files, prefix = '{} Detecting local files ({}/{}):'.format("✅" if index+1 == total_files else "➖", index + 1, total_files), suffix = 'Complete', length = 100)

    notionBookCollection.fetchAllBooks()

    # Process changes
    #     
    def get_property_value(list_book_formats, property):
        for item in list_book_formats:
            if hasattr(item, property) and getattr(item, property) not in [None, '']:
                return getattr(item, property)
        return ''
    
    def generateListBookFormats(matches):
        list_book_formats = []
        for match in matches:   # The order is important to get the properties
            if match.format.upper() in supported_formats and match.format.upper() == 'PAPER':
                list_book_formats.append(match)
            elif match.format.upper() in supported_formats and match.format.upper() == 'EPUB':
                list_book_formats.append(match)
            elif match.format.upper() in supported_formats and match.format.upper() == 'PDF':
                list_book_formats.append(match)
        return list_book_formats
    
    def generateBooksJson(list_book_formats, matches):
        generated_json = {
            "notion_page_id": get_property_value(list_book_formats, "notion_page_id"),
            "File Name": {"title": [{"text": {"content":  get_property_value(list_book_formats, "fileName")}}]},
            "Title": { "type": "rich_text", "rich_text": [{"type": "text", "text": {"content": get_property_value(list_book_formats, "title")},},],},
            "Format": {"type": "multi_select", "multi_select": [{"name": y} for y in [x.format for x in matches]]},
            "Publisher": { "type": "rich_text", "rich_text": [{"type": "text", "text": {"content": get_property_value(list_book_formats, "publisher")},},],},
            "Tags": {"type": "multi_select", "multi_select": [{"name": y} for y in matches[0].tags]},
            "Author": { "type": "rich_text", "rich_text": [{"type": "text", "text": {"content": get_property_value(list_book_formats, "author")},},],},
            "ISBN": { "type": "rich_text", "rich_text": [{"type": "text", "text": {"content": get_property_value(list_book_formats, "isbn")},},],},
        }
        return generated_json
    
    printProgressBar(0, localBookCollection.getLength(), prefix = '➖ {} books in Notion:'.format('Creating/updating' if exec_all else ('Creating' if args.only_new else 'Updating'),), suffix = 'Complete', length = 100)

    updated_count, created_count, deleted_count = 0, 0, 0
    for index, book in enumerate(localBookCollection.getAll()):
        if not book.ignore:
            local_matches = localBookCollection.findBook(book.fileName)
            local_list_book_formats = generateListBookFormats(local_matches)

            if notionBookCollection.existsByFileName(book.fileName):
                # Update
                if (args.only_updated or exec_all):
                    book.extractMetadata()
                    local_json = generateBooksJson(local_list_book_formats, local_matches)
                    notion_matches = notionBookCollection.findBook(book.fileName)
                    notion_list_book_formats = generateListBookFormats(notion_matches)
                    notion_json = generateBooksJson(notion_list_book_formats, notion_matches)
                    
                    notion_page_id = notion_json.pop("notion_page_id")
                    if not local_json == notion_json:
                        local_file_name = local_json.pop("File Name")
                        del local_json["notion_page_id"]
                        notionIntegration.update_page(local_json, page_id = notion_page_id)
                        my_logger.info("Updated page with id {} and File Name {}".format(notion_page_id, local_file_name))
                        updated_count += 1
            else:
                # Insert
                if (args.only_new or exec_all):
                    book.extractMetadata()
                    local_json = generateBooksJson(local_list_book_formats, local_matches)
                    del local_json["notion_page_id"]
                    local_json["Status"] = {"select": {"name": "Not Started"}}
                    notionIntegration.createPage(local_json)
                    my_logger.info("Created entry for File Name {}".format(local_json.get("File Name")))
                    created_count += 1
            for match in local_matches:
                match.ignore = True

        printProgressBar(index+1, localBookCollection.getLength(), prefix = '{} {} books in Notion ({}/{}):'.format(
            "✅" if index+1 == localBookCollection.getLength() else "➖",
            'Creating/updating' if exec_all else ('Creating' if args.only_new else 'Updating'),
            index+1,
            localBookCollection.getLength()),
            suffix = 'Complete',
            length = 100)
        
    # Delete from Notion the ones not found in local
    if (args.only_deleted or exec_all):
        printProgressBar(0, notionBookCollection.getLength(), prefix = '➖ Deleting books from Notion:', suffix = 'Complete', length = 100)
        for index, book in enumerate(notionBookCollection.getAll()):
            if not book.ignore:
                if not localBookCollection.existsByFileName(book.fileName):
                    notionIntegration.delete_page(book.notion_page_id)
                    my_logger.info("Deleted page with id {} and File Name {}".format(book.notion_page_id, book.fileName))
                    deleted_count += 1
                    for match in notionBookCollection.findBook(book.fileName):
                        match.ignore = True
            printProgressBar(index+1, notionBookCollection.getLength(), prefix = '{} Deleting books from Notion ({}/{}):'.format("✅" if index+1 == notionBookCollection.getLength() else "➖", index+1, notionBookCollection.getLength()), suffix = 'Complete', length = 100)

    print("\n- Created books: {}".format(created_count))
    my_logger.info("Created books: {}".format(created_count))
    print("- Updated books: {}".format(updated_count))
    my_logger.info("Updated books: {}".format(updated_count))
    print("- Deleted books: {}\n".format(deleted_count))
    my_logger.info("Deleted books: {}\n".format(deleted_count))

    print("- Log file {} created in {}\n".format(logs_file, logs_path))
    my_logger.info("FINISHED")
        



