import psycopg2
import os
import datetime
from coptracker import execute_queries

def write_to_heroku(booking_dates, results):
	conn = psycopg2.connect('postgres://ue99m6v4vbias0:pf653a3a598a4ef4d4d29c5758550a6a83f01b11185b16bf9643f8cbd0eba9da6@c8gfccabfmhkij.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dd8pufhjmc8q7j')
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
