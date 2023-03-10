import json
import base64

import requests
from urllib.parse import urlencode

from notion.exceptions import UnauthorizedError, WrongFormatInputError, ContactsLimitExceededError


class Client(object):
    URL = "https://api.notion.com/v1/"
    AUTH_ENDPOINT = "oauth/authorize?"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Notion-Version": "2022-06-28"}

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        if access_token is not None:
            self.set_token(access_token)
        if client_id and client_secret:
            self.CREDENTIALS = base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()

    def authorization_url(self, state=None):
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "owner": "user",
        }
        if state:
            params["state"] = state
        return self.URL + self.AUTH_ENDPOINT + urlencode(params)

    def get_access_token(self, code):
        body = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.REDIRECT_URI}
        headers = {"Authorization": f"Basic {self.CREDENTIALS}"}
        return self.post("oauth/token", data=json.dumps(body), headers=headers)

    def set_token(self, access_token):
        self.headers.update(Authorization=f"Bearer {access_token}")

    def get_current_user(self):
        return self.get("users/me")

    def list_users(self, page_size=None, start_cursor=None):
        params = {}
        if page_size:
            params["page_size"] = page_size
        if start_cursor:
            params["start_cursor"] = start_cursor
        return self.get("users", params=params)

    def list_objects(self, object_type, page_size=None, start_cursor=None):
        """
        object_type options are: page or database
        page_size: max 100 
        start_cursor: pagination variable, get this value from previous page 'next_cursor' parameter.
        """
        body = {"filter": {"value": object_type, "property": "object"}}
        if page_size:
            body["page_size"] = page_size
        if start_cursor:
            body["start_cursor"] = start_cursor
        return self.post("search", data=json.dumps(body))

    def get_database(self, database_id):
        return self.get(f"databases/{database_id}")

    def query_database_pages(
        self, database_id, filters: dict = None, sorts: dict = None, start_cursor=None, page_size=None
    ):
        body = {}
        if filters:
            body["filter"] = filters
        if sorts:
            body["sorts"] = sorts
        if start_cursor:
            body["start_cursor"] = start_cursor
        if page_size:
            body["page_size"] = page_size

        return self.post(f"databases/{database_id}/query", data=json.dumps(body))

    def create_page(self, database_id, properties, cover_url=None):
        body = {"parent": {"database_id": database_id}, "properties": properties}
        if cover_url:
            body["cover"] = {"external": {"url": cover_url}}
        return self.post("pages", data=json.dumps(body))

    def update_page(self, page_id, properties, cover_url=None):
        body = {"properties": properties}
        if cover_url:
            body["cover"] = {"external": {"url": cover_url}}
        
        return self.patch(f"pages/{page_id}", data=json.dumps(body))

    def get(self, endpoint, **kwargs):
        response = self.request("GET", endpoint, **kwargs)
        return self.parse(response)

    def post(self, endpoint, **kwargs):
        response = self.request("POST", endpoint, **kwargs)
        return self.parse(response)

    def delete(self, endpoint, **kwargs):
        response = self.request("DELETE", endpoint, **kwargs)
        return self.parse(response)

    def put(self, endpoint, **kwargs):
        response = self.request("PUT", endpoint, **kwargs)
        return self.parse(response)

    def patch(self, endpoint, **kwargs):
        response = self.request("PATCH", endpoint, **kwargs)
        return self.parse(response)

    def request(self, method, endpoint, headers=None, **kwargs):
        if headers:
            self.headers.update(headers)
        return requests.request(method, self.URL + endpoint, headers=self.headers, **kwargs)

    def parse(self, response):
        status_code = response.status_code
        if "Content-Type" in response.headers and "application/json" in response.headers["Content-Type"]:
            try:
                r = response.json()
            except ValueError:
                r = response.text
        else:
            r = response.text
        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 406:
            raise ContactsLimitExceededError(r)
        if status_code == 500:
            raise Exception
        return r
