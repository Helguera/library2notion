
import logging
from notion_client import Client
from notion_client import APIErrorCode, APIResponseError
from notion_client.errors import HTTPResponseError
from notion_client.helpers import collect_paginated_api
import time

class NotionIntegration:
    def __init__(self, notionToken, databaseId):
        self.token = notionToken
        self.client = Client(auth=self.token)
        self.database_id = databaseId

    def findPagesInDatabase(self, query = {}, retryIfError = False):
        while True:
            try:
                response = collect_paginated_api(self.client.databases.query, database_id=self.database_id)
                return response
            except (APIResponseError, HTTPResponseError, Exception) as error:
                print(error)
                print('Error finding pages from Notion...')
                if not retryIfError: return 0
                time.sleep(2) # Wait to send request again

    def createPage(self, properties, retry_if_error = False):
        while True:
            try:
                response = self.client.pages.create(parent={"database_id": self.database_id}, properties = properties)
                return response
            except (APIResponseError, HTTPResponseError, Exception) as error:
                print(error)
                if not retry_if_error: return 0
                time.sleep(2)    

    def update_page(self, properties, content = None, page_id = None, retry_if_error = False):
        while True:
            try:
                if page_id is None: page_id = self.notion_page_id
                response = self.client.pages.update(page_id=page_id, properties=properties)      

                if content is not None:
                    response = self.client.blocks.children.append(block_id = self.notion_page_id, children=content)
                return
            except (APIResponseError, HTTPResponseError, Exception) as error:
                print(error)
                if not retry_if_error: return 0
                time.sleep(2)  

    def delete_page(self, page_id, retry_if_error = False):
        while True:
            try:
                if page_id is None: page_id = self.notion_page_id
                response = self.client.pages.update(page_id=page_id, archived=True)
                return
            except (APIResponseError, HTTPResponseError, Exception) as error:
                print(error)
                if not retry_if_error: return 0
                time.sleep(2)
