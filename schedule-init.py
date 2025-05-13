import csv
import psycopg2
import os
import datetime
from datetime import date, timedelta
import json

connection_string = ''
today = date.today()
today_string = today.strftime('%b-%d-%Y')
print('Creating schedule for 2 days prior to ' + today_string)
date_to_be_processed = date.today() - timedelta(days=2)

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

# Find last date in table and iterrate to created missing dates
latest_query = "SELECT MAX(date) FROM schedule"
cur.execute(latest_query)
latest_response = cur.fetchone()
last_date = latest_response[0]

if last_date < date_to_be_processed:
    missing_days = (date_to_be_processed - last_date).days - 1
    print(missing_days)
    while missing_days >= 0:
	    date_string = (date_to_be_processed - timedelta(missing_days)).strftime('%m/%d/%Y')
	    create_query = "INSERT INTO schedule (date, drive_success, local_success, heroku_success) VALUES ('{}', FALSE, FALSE, FALSE)".format(date_string)
	    print(create_query)
	    cur.execute(create_query)
	    cur.execute("SELECT * FROM schedule ORDER BY date DESC")
	    print(cur.fetchone())
	    missing_days -= 1
conn.commit()
conn.close()
cur.close()

# New line for log
print('')
