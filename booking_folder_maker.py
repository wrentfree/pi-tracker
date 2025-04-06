from datetime import date
from datetime import timedelta
from drive_upload import *
from drive_file_search import *
from drive_create_folder import *
import json

booking_id = ''

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    booking_id = json_data['driveFolderId']

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

# print(get_folder(folder_name))
