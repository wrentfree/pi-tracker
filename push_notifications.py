import psycopg2
import os
import datetime
from datetime import date, timedelta
from pushbullet import Pushbullet
from schedule_methods import *
import json

pushbullet_id = ''
connection_string = ''
directory = '.'

# If there is a DIRECTORY env variable, set it here
if os.getenv("DIRECTORY"): directory = os.getenv("DIRECTORY")

with open(directory + '/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']
    pushbullet_id = json_data['pushbullet']

# Script to send push notification if there are any failures
def push_note():
    pb = Pushbullet(pushbullet_id)

    # push = pb.push_note("Test", 'Does this show up on my phone?')

    # Verifiy successes from schedule table
    schedule_date = date.today()-timedelta(days=2)
    schedule_string = schedule_date.strftime('%m/%d/%Y')
    schedule = Schedule(schedule_date)

    push_str = "Results for {}\n".format(schedule_string)

    # Local
    if schedule.local_success:
        push_str = push_str + 'Local Database succesfully executed\n'
    else:
        push_str = push_str + 'FAILURE on Local Database\n'

    # Heroku
    if schedule.heroku_success:
        push_str = push_str + 'Heroku Database succesfully executed\n'
    else:
        push_str = push_str + 'FAILURE on Heroku Database\n'

    # Drive
    if schedule.drive_success:
        push_str = push_str + 'Drive upload succesfully executed\n'
    else:
        push_str = push_str + 'FAILURE on Drive upload\n'

    schedule_results = schedule_check()
    if len(schedule_results):
        missing_dates = []
        for row in schedule_results:
            missing_dates.append(row['date'].strftime('%m/%d/%Y'))
        
        push_str = push_str + 'Data missing for ' + (', ').join(missing_dates) + '.\n'

    # Send push notification
    push = pb.push_note("Cop Tracker", push_str)
