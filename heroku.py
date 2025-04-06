import psycopg2
import os
import datetime
from bookings_tracker import execute_queries
import json

remote_string = ''
local_string = ''

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    remote_string = json_data['remotePostgres']
    local_string = json_data['localPostgres']

def write_to_heroku(booking_dates, results):
	conn = psycopg2.connect(remote_string)
	cur = conn.cursor()

	execute_queries(results['queries'], 'heroku', conn, cur)
	print('\nEntries written to heroku')

	conn = psycopg2.connect(local_string)
	cur = conn.cursor()
	for d in booking_dates:
		print(d)
		query = "UPDATE schedule SET heroku_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
