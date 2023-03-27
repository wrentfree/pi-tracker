import psycopg2
import os
import datetime
from datetime import date

conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
cur = conn.cursor()

today_string = date.today().strftime('%m/%d/%Y')
query = "SELECT local_success FROM schedule WHERE date='{}'".format(today_string)

cur.execute(query)
response = cur.fetchone()

# Convert tuple to str
response_str = ''.join(map(str, response)).lower()
print(response_str)

if response_str == 'true':
	print('no exception')
else:
	raise Exception("Retry")

