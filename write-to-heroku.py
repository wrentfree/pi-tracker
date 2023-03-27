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

conn = psycopg2.connect('host=ec2-44-213-151-75.compute-1.amazonaws.com user=ehzrohbdkkzvno password=2d510648de5837e946151984d4abfa9264a9ab35f075276d66cf3a18f1b02d74 dbname=d2c3huobn2rnjq')
cur = conn.cursor()

results = table_scrape(env_dates)
execute_queries(results['queries'], 'heroku', conn, cur)
print('\nEntries written to heroku')

if os.getenv('SCHEDULE').lower() == 'true':
	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	query = "UPDATE schedule SET heroku_success = TRUE WHERE date = '{}';".format(today.strftime('%m/%d/%Y'))
	cur.execute(query)
	conn.commit()
	conn.close()
	cur.close()
