# library2notion

[![PyPI version](https://img.shields.io/pypi/v/library2notion?label=version)](https://pypi.python.org/pypi/library2notion)
[![Python Version](https://img.shields.io/pypi/pyversions/library2notion.svg)](https://pypi.org/project/library2notion/)

A way to upload all your digital library in format .PDF or .EPUB to [Notion.so](https://notion.so). This tools will upload to a database in Notion relevant information from a digital library in order to make it easier to find books, add comments, filter by type or category and keep track of read ones.

This tool makes use of **csv2notion**, a tool created by [vzhd1701](https://github.com/vzhd1701/csv2notion).

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

Import/Merge your digital library collection in .PFD or .EPUB format to Notion.

general options:
  -p, --Path PATH                    Path where to start looking for books. It will also check all subfolders
  -l, --LogFilePath LOGFILEPATH      Location of the log file if exists. If not, a new one will be created in the specified location
  -e, --Extensions EXTENSIONS        List of extensions to be taken into account. At this moment .PDF and .EPUB are supported.
  -t, --NotionToken NOTIONTOKEN      Notion token, stored in token_v2 cookie for notion.so
  -u, --NotionDbUrl NOTIONDBURL      Notion DB URL
  -f, --ForceUpload FORCEUPLOAD      Force upload to Notion (if token and db url are provided) ignoring the log file. If no Notion data is provided it will generate the .csv file.
  -o, --OutputFolder OUTPUTFOLDER    Folder to store .csv, .xlsx, and deleted.json files. If not provided it will use './'
  -h, --help                         show this help message and exit
```

### Input

You must pass a starting path for the application to start searching for books with the `--Path` option. Also, a log file is needed if you have already executed the tool before. It can be passed with the `--LogFilePath` option. This log file will contain the status of previous execution so books that have already been scanned and upload won't be affected. If this log file is not provided, a new one will be created.

Optionally you can specify what book extensions you want the application to analyze with the option `--Extensions`. At this moment .PDF and .EPUB are supported.

If you want the application to upload the data to Notion, you must provide a URL to an existing Notion database with the `--NotionDbUrl` option; The URL must link to a database view, not a page.

The tool also requires you to provide a `token_v2` cookie for the Notion website through `--NotionToken` option.

**Important notice**. `token_v2` cookie provides complete access to your Notion account. Handle it with caution.

### Metadata

The tool will extract the following data to upload to Notion:

- **File Name**: is the full path to the file. It is used as primary key of the table in Notion, so it can't be duplicated.
- **Title**: title of the book.
- **Tags**: the categories of the book. They are generated automatically from the path. For example, if the path is `./Tech Books/Programming/Python/mybook.pdf`, the tags will be `Tech Books`, `Programming`, `Python`.
- **Author**: the author or authors of the book.
- **Publisher**: the publisher of the book.
- **Formats**: the available formats of the book. A book available in multiple formats will only appear once in the database. 
- **ISBN**: the ISBN.

### Columns

The tool will create a column per metadata extracted. Also, the following ones, which will be empty because they are only intended to be used in Notion, will be created:

- **Priority**: allows to select a priority and filter by that property in Notion.
- **Status**: the status of the book (reading, not started, on hold...)
- **Comments**: if we need to add some comments to the book
  
### Log File

The log file is a json file that contains info about the books that have already been uploaded to Notion. It will be automatically generated the first time the application is used. In next executions, if one or more files has been added to the path, the log file must be provided so the tool knows that only those new books have to be scanned and uploaded.

### Deleted Books

If a book is deleted from the path, the tool will detect it the next time it is executed (only, of course, if a log file is provided). This will generate a `deleted.json` file in the ouput folder with the deleted books. But, **really important**, the book will not be deleted from Notion. That has to be done manually.

## csv2notion

This tool analizes books and creates a .csv file with the results. The task of uploading the data to Notion is performed by the tool [csv2notion](https://github.com/vzhd1701/csv2notion).

## Getting help

If you found a bug or have a feature request, please [open a new issue](https://github.com/helguera/library2notion/issues/new/choose).

If you have a question about the program or have difficulty using it, you are welcome to [the discussions page](https://github.com/helguera/library2notion/discussions). You can also mail me directly at [javier@javierhelguera.com](mailto:javier@javierhelguera.com), I'm always happy to help.