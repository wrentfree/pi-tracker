import csv
import psycopg2
import os
import datetime
from datetime import date, timedelta
import json

connection_string = ''

with open('config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

#Changed to show the actual day being tracked
today_string = (date.today() - timedelta(days=2)).strftime('%m/%d/%Y')
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
