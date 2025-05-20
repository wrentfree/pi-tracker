import psycopg2
import os
import datetime
from bookings_tracker import Booking
from drive_methods import *
import json
import copy

directory = '.'

# If there is a DIRECTORY env variable, set it here
if os.getenv("DIRECTORY"): directory = os.getenv("DIRECTORY")

remote_string = ''
local_string = ''

with open(directory + '/config.json') as f:
    json_data = json.load(f)
    remote_string = json_data['remotePostgres']
    local_string = json_data['localPostgres']


def write_to_local(results):
	
	conn = psycopg2.connect(local_string)
	conn.autocommit = True
	cur = conn.cursor()
	
	for booking in results:
		if booking.success:
			execute_queries(booking.queries, 'local', conn, cur)
			print('\nEntries written to local for ' + booking.formatted_date)
			
			query = "UPDATE schedule SET local_success = TRUE WHERE date = '{}';".format(booking.formatted_date)
			cur.execute(query)
	conn.close()
	cur.close()

def write_to_heroku(results):
	conn = psycopg2.connect(remote_string)
	conn.autocommit = True
	cur = conn.cursor()
	
	for booking in results:
		if booking.success:
			execute_queries(booking.queries, 'heroku', conn, cur)
			print('\nEntries written to heroku for ' + booking.formatted_date)
			
			# Update schedule on local
			conn.close()
			cur.close()
			conn = psycopg2.connect(local_string)
			cur = conn.cursor()
			query = "UPDATE schedule SET heroku_success = TRUE WHERE date = '{}';".format(booking.formatted_date)
			cur.execute(query)
			conn.commit()
	conn.close()
	cur.close

def write_to_drive(results):
	# If folder exists and is in the 'Bookings' folder, upload file to folder
	# else create folder in the 'Bookings' folder and upload file to folder
	
	conn = psycopg2.connect(local_string)
	conn.autocommit = True
	cur = conn.cursor()
	
	for booking in results:
		if booking.success:
			booking.write_csv()
			folder_id = get_folder('Bookings ' + booking.date_object.strftime('%b-%Y'))
			file_name = booking.csv_title
			upload_to_folder(real_folder_id=folder_id, file_name=file_name, file_type="text/csv")
			
			query = "UPDATE schedule SET drive_success = TRUE WHERE date = '{}';".format(booking.formatted_date)
			cur.execute(query)
	conn.close()
	cur.close()

def write_to_all(results):
	write_to_local(copy.deepcopy(results))
	write_to_heroku(copy.deepcopy(results))
	write_to_drive(copy.deepcopy(results))


def execute_queries(queries, db, conn, cur):
    for query in queries:
        try:
            cur.execute(query)
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
        else:
            conn.commit()
            #print('autocommited')