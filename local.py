import psycopg2
import os
import datetime
from coptracker import execute_queries


def write_to_local(booking_dates, results):
	
	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()

	execute_queries(results['queries'], 'local', conn, cur)
	print('\nEntries written to local')

	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	for d in booking_dates:
		query = "UPDATE schedule SET local_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
