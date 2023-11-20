from coptracker import *
import datetime
import os

def write_to_drive(booking_dates, results):
	# If folder exists and is in the 'Bookings' folder, upload file to folder
	# else create folder in the 'Bookings' folder and upload file to folder
	table_info = results

	dates_info = table_info['dates_info']

	for day_info in dates_info:
		print(day_info)
		folder_id = get_folder('Bookings ' + day_info['date_info'].strftime('%b-%Y'))
		file_name = day_info['csv']
		upload_to_folder(real_folder_id=folder_id, file_name=file_name, file_type="text/csv")

	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	for d in booking_dates:
		query = "UPDATE schedule SET drive_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
