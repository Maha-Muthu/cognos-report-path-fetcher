# Importing Required Libraries
import requests
import json
from getpass import getpass
import pandas as pd
import os

#User Prompt for Namespace, Username, Password and Base URL
namespace = input("Enter Cognos Namespace: ")
username = input("Enter Username: ")
password = getpass("Enter Password:  ")
base_url = input("Enter Base URL (http://<cognos_analytics_server>:<port>): ")

# IBM Cognos http://<cognos_analytics_server>:<port>/api/api-docs/
session_endpoint = "/api/v1/session"
content_endpoint = "/api/v1/content"
items_endpoint = "/api/v1/content/{id}/items"

# Request Payload for Access Token
payload = json.dumps({
  "parameters": [
    {
      "name": "CAMNamespace",
      "value": namespace
    },
    {
      "name": "CAMUsername",
      "value": username
    },
    {
      "name": "CAMPassword",
      "value": password
    }
  ]
})
session_headers = {
  'accept': 'application/json',
  'Content-Type': 'application/json',
  'Cache-Control': 'no-cache'
}

# Fetch Access Token
try :
  session_response = requests.request("PUT", base_url+session_endpoint, headers=session_headers, data=payload)

except Exception as exception:
  print(exception)
  exit()

if(session_response.status_code!=201):
  print(session_response.content)
  exit()

# Request Payload for fecthing Root Folders from Content Store
token = session_response.cookies.get('XSRF-TOKEN')
cookies = '; '.join([f'{name}={value}' for name, value in session_response.cookies.items()])

content_headers = {
  'X-XSRF-Token': token,
  'Cookie': cookies
}

content_response = requests.request("GET", base_url+content_endpoint, headers=content_headers)

root_folders = (json.loads(content_response.text))['content']

parent_folders=[]

# This Application Extracts Root Folders Which Include the term "team", Update Here to change the filter for the Root Folder
for root_folder in root_folders:
  if "team" in root_folder['defaultName'].lower():
    parent_folders.append(root_folder['id'])

folder_contents ={}

# Method to De-Serializes Response from Cognos API
def content_extractor(response):
  response_contents = (json.loads(response.text))['content']
  global folder_contents
  folder_contents ={}
  for response_content in response_contents:
    folder_contents[response_content['defaultName']]=[response_content['id'],response_content['type']]
  return folder_contents

# Method to make API Call
def api_call(id):
  content_item_response = requests.request("GET", base_url+items_endpoint.format(id=id), headers=content_headers)
  folder_contents=content_extractor(content_item_response)
  return folder_contents

# Recursive Method to fetch all files from folders in Root Folder
def fetch_all_files(folder_id, path='/content'):
  items = api_call(folder_id)
  files = [{'name': item, 'path':path+"/"+folder_contents[item][1]+"[@name='"+item+"']"} for item in items if folder_contents[item][1] == 'report']
  folders = [{'id': folder_contents[item][0], 'name': item, 'type': folder_contents[item][1]} for item in items if folder_contents[item][1] == 'folder']

  for folder in folders:
    files.extend(fetch_all_files(folder['id'], path+"/"+folder['type']+"[@name='"+folder['name']+"']"))

  return files

# Method to write Report Name and Report Path to Excel
def write_to_excel(data):
  filename = "output.xlsx"
  df = pd.DataFrame(data)
  if os.path.exists(filename):
    os.remove(filename)
  writer = pd.ExcelWriter(filename)
  df.to_excel(writer, index=False)
  writer._save()

files=[]
for parent_folder in parent_folders:
  print("Retrieving all Reports from "+parent_folder)
  reports_path=[]
  reports_title=[]
  files = fetch_all_files(parent_folder)
  search_folder = input("Enter The Folder to Fetch Reports Under "+parent_folder+" Or enter 'all' to fecth all Reports: ")
  
  if search_folder == 'all':
    data = {'Report Title': [file['name'] for file in files],
        'Report Path': [file['path'] for file in files]}
    write_to_excel(data)

  else:
    for file in files:
      if ("folder[@name='{id}']".format(id=search_folder) in file['path']):
        reports_title.append(file['name'])
        reports_path.append(file['path'])
    data = {'Report Title': reports_title,
        'Report Path': reports_path}
    write_to_excel(data)
    