import psycopg2
import os
import datetime
from datetime import date
from pushbullet import Pushbullet

# Script to send push notification if there are any failures
pb = Pushbullet('o.CL45Xw9qtRCMmYiNzjLXxb7mjMVZUdg8')

# push = pb.push_note("Test", 'Does this show up on my phone?')

# Verifiy successes from schedule table

conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
cur = conn.cursor()

today_string = date.today().strftime('%m/%d/%Y')
query = "SELECT local_success,heroku_success,drive_success FROM schedule WHERE date='{}'".format(today_string)

cur.execute(query)
response = cur.fetchone()

# Convert tuple to str
response_str = ', '.join(map(str, response)).lower()
response_arr = response_str.split(', ')

push_str = ''

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

push = pb.push_note("Cop Tracker", push_str)
