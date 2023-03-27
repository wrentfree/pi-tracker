import csv
import psycopg2
import os
import datetime
from datetime import date

conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
cur = conn.cursor()

today_string = date.today().strftime('%m/%d/%Y')
query = "SELECT COUNT(*) FROM schedule WHERE date='{}'".format(today_string)

cur.execute(query)
response = cur.fetchone()

# Convert tuple to int
response_int = int(''.join(map(str, response)))
if response_int == 0:
	create_query = "INSERT INTO schedule (date, drive_success, local_success, heroku_success) VALUES ('{}', FALSE, FALSE, FALSE)".format(today_string)
	cur.execute(create_query)
	cur.execute("SELECT * FROM schedule")
	print(cur.fetchone())

conn.commit()
conn.close()
cur.close()
