import psycopg2
import os
import datetime
from datetime import date, timedelta
from pushbullet import Pushbullet
import json

pushbullet_id = ''
connection_string = ''

with open('/home/wren/Desktop/pi-tracker/pi-tracker/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']
    pushbullet_id = json_data['pushbullet']

# Script to send push notification if there are any failures
pb = Pushbullet(pushbullet_id)

# push = pb.push_note("Test", 'Does this show up on my phone?')

# Verifiy successes from schedule table

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

today_string = (date.today()-timedelta(days=2)).strftime('%m/%d/%Y')
query = "SELECT local_success,heroku_success,drive_success FROM schedule WHERE date='{}'".format(today_string)

cur.execute(query)
response = cur.fetchone()

# Convert tuple to str
response_str = ', '.join(map(str, response)).lower()
response_arr = response_str.split(', ')

push_str = "Results for {}\n".format(today_string)

# Local
if response_arr[0] == 'true':
	push_str = push_str + 'Local Database succesfully executed\n'
else:
	push_str = push_str + 'FAILURE on Local Database\n'

# Heroku
if response_arr[1] == 'true':
	push_str = push_str + 'Heroku Database succesfully executed\n'
else:
	push_str = push_str + 'FAILURE on Heroku Database\n'

# Drive
if response_arr[2] == 'true':
	push_str = push_str + 'Drive upload succesfully executed\n'
else:
	push_str = push_str + 'FAILURE on Drive upload\n'

# Missing data
missing_query = """
    SELECT date FROM schedule
    WHERE local_success = FALSE
    OR heroku_success = FALSE
    OR drive_success = FALSE
"""
cur.execute(missing_query)
missing_response = cur.fetchall()

if len(missing_response):
    missing_dates = []
    print(len(missing_response))
    for row in missing_response:
	    print(row)
	    missing_dates.append(row[0].strftime('%m/%d/%Y'))
    
    push_str = push_str + 'Data missing for ' + (', ').join(missing_dates) + '.\n'

# Send push notification
push = pb.push_note("Cop Tracker", push_str)
