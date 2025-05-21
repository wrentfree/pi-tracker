from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import google.auth
from googleapiclient.http import MediaFileUpload
from datetime import date
from datetime import timedelta
import json
import os

directory = '.'

# If there is a DIRECTORY env variable, set it here
if os.getenv("DIRECTORY"): directory = os.getenv("DIRECTORY")

booking_id = ''

with open(directory + '/config.json') as f:
    json_data = json.load(f)
    booking_id = json_data['driveFolderId']


def create_folder(folder_name, parent_id):
    """ Create a folder and prints the folder ID
    Returns : Folder Id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = Credentials.from_authorized_user_file(directory + '/token.json')

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder has created with ID: "{file.get("id")}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')

# Searches for a folder in google drive    
def search_file(query):
    # Search file in drive location
    creds = Credentials.from_authorized_user_file(directory + '/token.json')


    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(F'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files

# Checks if file or folder is in a specific folder
def is_in_folder(parent_id, child_id):
    creds = Credentials.from_authorized_user_file(directory + '/token.json')

    try:
        # create drive api client
        service = build('drive', 'v2', credentials=creds)
        service.parents().get(fileId=child_id, parentId=parent_id).execute()

    except HttpError as error:
        if error.resp.status == 404:
            return False
        else:
            print('An error occurred: %s' % error)
            raise error
    return True

# Search for folder by name. If it does not exist in the Bookings folder, create it.
# Returns folder id.
# Format for bookings: 'Bookings %b-%Y'
def get_folder(folder_name):
    files = search_file(query="name='" + folder_name + "'")
    if len(files) > 0:
        # If folder exists, is it in the 'Bookings' folder?
        for file in files:
            file_id = file['id']
            if is_in_folder(parent_id=booking_id,
                            child_id=file_id):
                # The folder is in the bookings folder, return folder's file id
                return file_id
    # Folder does not exist. Create folder and return id
    new_folder_id = create_folder(folder_name=folder_name,
                                  parent_id=booking_id)
    return new_folder_id

def upload_to_folder(real_folder_id, file_name, file_type):
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder, name of the file to be uploaded, the type of the file to be uploaded
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = Credentials.from_authorized_user_file(directory + '/token.json')

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        folder_id = real_folder_id
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_name,
                                mimetype=file_type, resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File with ID: "{file.get("id")}" has added to the folder with '
              F'ID "{real_folder_id}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')
