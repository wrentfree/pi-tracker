import psycopg2
import os
import datetime
from bookings_tracker import execute_queries
import json

connection_string = ''

with open('config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']


def write_to_local(booking_dates, results):
	
	conn = psycopg2.connect(connection_string)
	cur = conn.cursor()

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
