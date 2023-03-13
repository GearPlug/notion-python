# notion-python
![](https://img.shields.io/badge/version-0.1.0-success) ![](https://img.shields.io/badge/Python-3.8%20|%203.9%20|%203.10%20|%203.11-4B8BBE?logo=python&logoColor=white)
  
*notion-python* is an API wrapper for Notion, written in Python.  
This library uses Oauth2 for authentication.
## Installing
```
pip install notion-python-2
```
## Usage
* If you don't have an access token:
```
from notion.client import Client
client = Client(client_id, client_secret, redirect_uri)
```
To obtain and set an access token, follow this instructions:
1. **Get authorization URL**
```
url = client.authorization_url()
```
2. **Get access token using code**
```
response = client.get_access_token(code)
```
3. **Set access token**
```
client.set_token(access_token)
```  
Check more information about Notion Oauth: https://developers.notion.com/docs/authorization  

* If you already have an access token:
```
from notion.client import Client
client = Client(access_token=access_token)
```
### User
#### - Get Current User
```
user = client.get_current_user()
```
#### - List users
```
users = client.list_users(page_size=3)
# page_size: max 100 
# start_cursor: pagination variable, get this value from previous page 'next_cursor' parameter.
```
### Databases and Pages
#### - List all objects
```
# object_type options are: page or database
# page_size: max 100 
# start_cursor: pagination variable, get this value from previous page 'next_cursor' parameter.

databases_list = client.list_objects("database", page_size=5)
```
#### - Get database
```
database = client.get_database(database_id)
```
#### - Query database pages
How to build a filter object: https://developers.notion.com/reference/post-database-query-filter  
How to build a sort object: https://developers.notion.com/reference/post-database-query-sort
```
filter_criteria = {"property": "Main Email", "email": {"equals": "example@mail.com"}}
# Where 'Main Email' is the field name and 'email' is the field type
pages = client.query_database_pages(
    database_id, 
    filters=filter_criteria, 
    sorts: dict = None, 
    start_cursor=None, 
    page_size=None
)
```
#### - Create page
```
properties_example = {
    "Project name": {
        "title": [
            {
                "text": {
                    "content": "First project built with this library"
                    }
            }
        ]
    },
}
cover_url = "https://upload.wikimedia.org/wikipedia/commons/1/1/example.jpg"
page = client.create_page(database_id, properties_example, cover_url=cover_url)
```
#### - Update page
```
properties_example = {
    "Project name": {
        "title": [
            {
                "text": {
                    "content": "Project field modified"
                    }
            }
        ]
    },
}
page = client.update_page(page_id, properties_example, cover_url=None)
```
How to build a properties object: https://developers.notion.com/reference/page-property-values
