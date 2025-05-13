import csv
import psycopg2
import os
import datetime
from datetime import date, timedelta
import json

# This script runs daily to create entries in the schedule table
# for tracking successes or failures for each day

connection_string = ''
today = date.today()
today_string = today.strftime('%b-%d-%Y')

directory = '/home/wren/Desktop/pi-tracker/pi-tracker/'

# If there is a DIRECTORY env variable, set it here
if os.getenv("DIRECTORY"): directory = os.getenv("DIRECTORY")

with open(directory + 'config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']

#Returns [(date, local_success, heroku_success, drive_success)] in list of
#tuples
def schedule_check():
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    today_string = date.today().strftime('%m/%d/%Y')
    query = "SELECT date, local_success, heroku_success, drive_success FROM schedule WHERE local_success = FALSE OR heroku_success = FALSE OR drive_success = FALSE"
    cur.execute(query)
    response = cur.fetchall()

    conn.close()
    cur.close()
    return response


def schedule_init():
    
    print('Creating schedule for 2 days prior to ' + today_string)
    date_to_be_processed = date.today() - timedelta(days=2)
    
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

# If this file is being run directly, run schedule_init
if __name__ == '__main__':
    schedule_init()
