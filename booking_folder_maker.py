from datetime import date
from datetime import timedelta
from drive_upload import *
from drive_file_search import *
from drive_create_folder import *

booking_id = '1z_QtU4t1iaAOowzpQPfyv2iKEGnKh9ND'


# Create Folder name
folder_month = (date.today() - timedelta(days=1)).strftime('%b-%Y')
folder_name = 'Bookings ' + folder_month


# Search for folder by name. If it does not exist in the Bookings folder, create it.
# Returns folder id.
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