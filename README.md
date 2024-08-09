# library2notion

[![PyPI version](https://img.shields.io/pypi/v/library2notion?label=version)](https://pypi.python.org/pypi/library2notion)
[![Python Version](https://img.shields.io/pypi/pyversions/library2notion.svg)](https://pypi.org/project/library2notion/)

A tool to create a library on Notion with all your books (digital or not) in order to make it easier to find them, add comments, priorities, filter by type or category and keep track of read ones.

Main features:
- Detects all digital books from a given path and all the subfolders.
- Adds, updates or deletes entries on Notion DB to match the status of the local folder.
- Possibility to create a simple .paper file to add non-digital to be tracked as well.
- Extracts metadata from .pdf and .epub files.

## Installation

### Using portable binary

[**Download the latest binary release**](https://github.com/helguera/library2notion/releases/latest).

### With [Homebrew](https://brew.sh/) (Recommended for macOS)

```bash
$ brew install helguera/tap/library2notion
```

### With [PIPX](https://github.com/pypa/pipx) (Recommended for Linux & Windows)

```shell
$ pipx install library2notion
```

### With PIP

```bash
$ pip install --user library2notion
```

**Python 3.7 or later required.**

### From source

This project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.

```shell
$ git clone https://github.com/helguera/library2notion.git
$ cd library2notion/
$ poetry install
$ poetry run library2notion
```

## Usage

```plain
$ library2notion --help
usage: library2notion [-h] -p PATH [-l LOGFILEPATH] [-e EXTENSIONS [EXTENSIONS ...]] [-t NOTIONTOKEN] [-u NOTIONDBURL] [-f] [-o OUTPUTFOLDER]

library2notion created by Javier Helguera (github.com/helguera) © 2023 MIT License

general options:
  -p, --Path PATH                    Path where to start looking for books. It will also check all subfolders
  -t, --NotionToken NOTIONTOKEN      Notion token
  -d, --NotionDbId  NOTIONDBURL      Notion database id
  -f, --Formats     FORMATS          List of formats to be taken into account. At this moment .PDF, .EPUB and .PAPER are supported
  -c, --Config      CONFIG           Provide a config json which includes the parameters
  -i, --Ignore      IGNORE           Folders to ignore (in a list)  
  -only_new,                         Only check new books
  -only_updated                      Only check changes in existing books (does not include removals)
  -only_deleted                      Only check deleted books
  -h, --help                         Show this help message and exit
```

## Input

### -p, --Path

The path where to look for files (and subfolders). It is higly recommended to use relative paths. This is really important since it will also be used to generate the tags of each book. (Take a look at "Metadata" section for further info).

For example, if your library looks like:
```plain
/home/your_user/Documents/books/Programming/Python
/home/your_user/Documents/books/Programming/C
/home/your_user/Documents/books/History/Spanish History
```
They ideal way to proceed is, first, move to `books` folder, since it is the common one for all books.
```plain
cd /home/your_user/Documents/books
```
And from here, execute l2n with a relative path:
```plain
library2notion -p "./"
```
They way a book is uniquely identified is by using its path. This is important because the book `./books/Programming/Python/PythonCookbook` will be treated as a different one from `./Programming/Python/PythonCookbook`.

### -t, --NotionToken

It is the secret token from Notion when an itegration is created. Visit [the official docs](https://developers.notion.com/docs/create-a-notion-integration) for further info. Don't forget to [give your integration page permissions](https://developers.notion.com/docs/create-a-notion-integration#give-your-integration-page-permissions).

### -d, --NotionDbId

The id of the Notion database where all info will be uploaded. This database has to exist in advance and the columns it needs to have are fixed and **can't be changed**. These are:

| Column Name | Type         |
|-------------|--------------|
| File Name   | Title        |
| Title       | Text         |
| Priority    | Select       |
| Status      | Select       |
| Format      | Multi-select |
| Tags        | Multi-select |
| Comments    | Text         |
| Author      | Text         |
| Publisher   | Text         |
| ISBN        | Text         |

To get the database ID value, open the database as a full page in Notion. Use the Share menu to Copy link. Now paste the link in your text editor so you can take a closer look. The URL uses the following format:

```plain
https://www.notion.so/{workspace_name}/{database_id}?v={view_id}
```

### -f, --Formats

These are the formats that will be taken into account. At this moment, **.epub, .pdf and .paper** are supported and used by default.
```plain
library2notion -f EPUB PAPER  -> only look for .epub and .paper files
library2notion -f PDF         -> only look for .pdf files
```

### -c, --Config

A config.json file can be provided as input with the settings already in it. The tool will ask if you want it to create this file for you the first time it is executed, so future executions will be easier.

```json
{
    "notion_secret_token": "",
    "notion_db_id": "",
    "path": "",
    "ignore": []
}
```

### -i, --Ignore

This allows you to exlude some folders or subfolders that you don't want to include. For example:

```plain
-i History "./Tech Books/Programming" 
```
The folder "History" will be completely ignored. Same for "Tech Books/Programming", but not for the rest of the books in  "Tech Books".

### -only_new

Checks only new books that have been added to the path since the last execution. Skips updated and deleted ones.

### -only_updated

Checks only books that have been updated since the last execution. Skips new and deleted ones.

### -only_deleted

Checks only books that have been deleted since the last execution. Skips new and updated ones.

## Metadata

The tool will extract the following data to upload to Notion:

- **File Name**: is the full path to the file. It is used as primary key of the table in Notion, so it can't be duplicated.
- **Title**: title of the book.
- **Tags**: the categories of the book. They are generated automatically from the path. For example, if the path is `./Tech Books/Programming/Python/mybook.pdf`, the tags will be `Tech Books`, `Programming`, `Python`.
- **Author**: the author or authors of the book.
- **Publisher**: the publisher of the book.
- **Formats**: the available formats of the book. A book available in multiple formats will only appear once in the database.
- **ISBN**: the ISBN.

## Non-digital books (.paper)

With update 0.2.0, the tool supports non-digital books. You just have to create a `.paper` file in a folder per non-digital book that you want to add with the following content:

```json
{
    "Title": "",
    "Author": "",
    "Publisher": "",
    "ISBN": ""
}
```

## Log Files

A log file will be created after each execution in folder `./library2notion-logs`. It will include info about created, updated and deleted books.

## Examples

### First example

### Second example

### Third example

## Getting help

If you found a bug or have a feature request, please [open a new issue](https://github.com/helguera/library2notion/issues/new/choose).

If you have a question about the program or have difficulty using it, you are welcome to [the discussions page](https://github.com/helguera/library2notion/discussions). You can also mail me directly at [javier@javierhelguera.com](mailto:javier@javierhelguera.com), I'm always happy to help.