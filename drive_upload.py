from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def upload_to_folder(real_folder_id, file_name, file_type):
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder, name of the file to be uploaded, the type of the file to be uploaded
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = Credentials.from_authorized_user_file('/home/wren/Desktop/pi-tracker/pi-tracker/token.json')

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


if __name__ == '__main__':
    upload_to_folder(real_folder_id='', \
                     file_name="Oct-09-2022.csv", \
                     file_type="text/csv")