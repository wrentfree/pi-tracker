from bookings_tracker import *
import datetime
import os
import json

connection_string = ''

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']

def write_to_drive(results):
	# If folder exists and is in the 'Bookings' folder, upload file to folder
	# else create folder in the 'Bookings' folder and upload file to folder
	
	conn = psycopg2.connect(connection_string)
	conn.autocommit = True
	cur = conn.cursor()
	
	for date_info in results:
		if date_info['success']:
			folder_id = get_folder('Bookings ' + date_info['date_info'].strftime('%b-%Y'))
			file_name = date_info['csv']
			upload_to_folder(real_folder_id=folder_id, file_name=file_name, file_type="text/csv")
			
			query = "UPDATE schedule SET drive_success = TRUE WHERE date = '{}';".format(date_info['formatted_date'])
			cur.execute(query)
			#conn.commit()
	conn.close()
	cur.close()
	
	"""
	table_info = results

	dates_info = table_info['dates_info']

	for day_info in dates_info:
		print(day_info)
		folder_id = get_folder('Bookings ' + day_info['date_info'].strftime('%b-%Y'))
		file_name = day_info['csv']
		upload_to_folder(real_folder_id=folder_id, file_name=file_name, file_type="text/csv")

	conn = psycopg2.connect(connection_string)
	cur = conn.cursor()
	for d in booking_dates:
		query = "UPDATE schedule SET drive_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
	"""
