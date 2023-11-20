import psycopg2
import os
import datetime
from coptracker import execute_queries

def write_to_heroku(booking_dates, results):
	conn = psycopg2.connect('host=ec2-44-213-151-75.compute-1.amazonaws.com user=ehzrohbdkkzvno password=2d510648de5837e946151984d4abfa9264a9ab35f075276d66cf3a18f1b02d74 dbname=d2c3huobn2rnjq')
	cur = conn.cursor()

	execute_queries(results['queries'], 'heroku', conn, cur)
	print('\nEntries written to heroku')

	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	for d in booking_dates:
		print(d)
		query = "UPDATE schedule SET heroku_success = TRUE WHERE date = '{}';".format(d)
		cur.execute(query)
		conn.commit()
	conn.close()
	cur.close()
