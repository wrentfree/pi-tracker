import csv
import psycopg2
import os
import datetime
from coptracker import table_scrape, execute_queries

today = datetime.datetime.now()
delta = datetime.timedelta(days = 2)
date = today - delta
env_dates = [date]
if os.getenv('DATES'):
	env_dates = os.getenv('DATES').split(',')

conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
cur = conn.cursor()

results = table_scrape(env_dates)
execute_queries(results['queries'], 'local', conn, cur)
print('\nEntries written to local')

if os.getenv('SCHEDULE').lower() == 'true':
	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	query = "UPDATE schedule SET local_success = TRUE WHERE date = '{}';".format(today.strftime('%m/%d/%Y'))
	cur.execute(query)
	conn.commit()
	conn.close()
	cur.close()
