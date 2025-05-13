import psycopg2
import os
import datetime
from bookings_tracker import execute_queries
import json

connection_string = ''

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']


def write_to_local(results):
	
	conn = psycopg2.connect(connection_string)
	conn.autocommit = True
	cur = conn.cursor()
	
	for date_info in results:
		if date_info['success']:
			execute_queries(date_info['queries'], 'local', conn, cur)
			print('\nEntries written to local')
			
			query = "UPDATE schedule SET local_success = TRUE WHERE date = '{}';".format(date_info['formatted_date'])
			cur.execute(query)
			#conn.commit()
	conn.close()
	cur.close()
	"""
	execute_queries(results['queries'], 'local', conn, cur)
	print('\nEntries written to local')

	conn = psycopg2.connect(connection_string)
	cur = conn.cursor()
	for d in booking_dates:
		query = "UPDATE schedule SET local_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
	"""
