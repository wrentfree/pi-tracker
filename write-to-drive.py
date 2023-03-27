from coptracker import *

# If folder exists and is in the 'Bookings' folder, upload file to folder
# else create folder in the 'Bookings' folder and upload file to folder
file_name = table_scrape()['csv_title']
folder_id = get_folder(folder_name)
upload_to_folder(real_folder_id=folder_id, \
                 file_name=file_name, \
                 file_type="text/csv")
