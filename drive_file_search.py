from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


def search_file(query):
    # Search file in drive location
    creds = Credentials.from_authorized_user_file('/home/wren/Desktop/pi-tracker/pi-tracker/token.json')


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

def is_in_folder(parent_id, child_id):
    creds = Credentials.from_authorized_user_file('/home/wren/Desktop/pi-tracker/pi-tracker/token.json')

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


if __name__ == '__main__':
    print(search_file(query="name='Oct-07-2022.csv'"))
    print(is_in_folder(parent_id='1z_QtU4t1iaAOowzpQPfyv2iKEGnKh9ND',
                 child_id='1uWgExsYQWrtMe5GHSbfPpCMBnezYF0Yp'))