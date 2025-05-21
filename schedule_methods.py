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
date_to_be_processed = date.today() - timedelta(days=2)

directory = '.'

# If there is a DIRECTORY env variable, set it here
if os.getenv("DIRECTORY"): directory = os.getenv("DIRECTORY")

with open(directory + '/config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostgres']

class Schedule:
    """Class for helping handle schedule

    Parameter
    ---------
    date_object : datetime.date
        The date to be checked on the schedule
    local_success : bool (optional)
    heroku_success : bool (optional)
    drive_success : bool (optional)
    
    Attributes
    ----------
    date_object : date
    local_success : bool
    heroku_success : bool
    drive_success : bool
    """
    def __init__(self, date_object, local_success = None, heroku_success = None, drive_success = None):
        self.date_object = date_object
        self.local_success = local_success
        self.heroku_success = heroku_success
        self.drive_success = drive_success
        if local_success is None or heroku_success is None or drive_success is None:
            result = schedule_check(date_object)[0]
            self.local_success = result['local_success']
            self.heroku_success = result['heroku_success']
            self.drive_success = result['drive_success']


# Parses any date strings passed as environment variables and returns
# date objects
def check_dates(dates=[]):
    env_dates = []
    if os.getenv('DATES') == ['all']:
         env_dates = 'all'
    elif os.getenv('DATES'):
        env_dates = os.getenv('DATES').split(',')
        format_dates = []
        for date_info in env_dates:
            format_dates.append(datetime.datetime.strptime(date_info, '%m/%d/%Y'))
        env_dates = format_dates
    elif len(dates) > 0:
        format_dates = []
        for date_info in dates:
            if type(date_info) is str:
                format_dates.append(datetime.datetime.strptime(date_info, '%m/%d/%Y'))
            elif type(date_info) is datetime.datetime:
                format_dates.append(date_info)
        env_dates = format_dates
    else:
        env_dates = [date_to_be_processed]
    return env_dates

# Returns [{'date':, 'local_success':, 'heroku_success':, 'drive_success':}] in list of
# dictionaries for dates where there was a failure if no argument is passed.
# Otherwise, returns the schedule results for that date.
def schedule_check(date_object = None):
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    query = "SELECT date, local_success, heroku_success, drive_success FROM schedule WHERE local_success = FALSE OR heroku_success = FALSE OR drive_success = FALSE"
    if date_object:
        query = "SELECT date, local_success, heroku_success, drive_success FROM schedule WHERE date = '" + date_object.strftime('%m/%d/%Y') +"'"
    cur.execute(query)
    response = cur.fetchall()

    conn.close()
    cur.close()
    dict_list = []
    # print(response)
    for row in response:
        dict_list.append({'date':row[0], 'local_success':row[1], 'heroku_success':row[2], 'drive_success': row[3]})
    return dict_list


def schedule_init():
    date_to_be_processed = date.today() - timedelta(days=2)
    processed_string = date_to_be_processed.strftime('%b-%d-%Y')
    
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    
    # Find last date in table and iterrate to created missing dates
    latest_query = "SELECT MAX(date) FROM schedule"
    cur.execute(latest_query)
    latest_response = cur.fetchone()
    last_date = latest_response[0]
    
    if last_date < date_to_be_processed:
        print('Creating schedule for missing days leading up to and including' + processed_string)
        missing_days = (date_to_be_processed - last_date).days - 1
        while missing_days >= 0:
            date_string = (date_to_be_processed - timedelta(missing_days)).strftime('%m/%d/%Y')
            create_query = "INSERT INTO schedule (date, drive_success, local_success, heroku_success) VALUES ('{}', FALSE, FALSE, FALSE)".format(date_string)
            print(create_query)
            cur.execute(create_query)
            cur.execute("SELECT * FROM schedule ORDER BY date DESC")
            print(cur.fetchone())
            missing_days -= 1
        # New line for log
        print('')
    conn.commit()
    conn.close()
    cur.close()

# If this file is being run directly, run schedule_init
if __name__ == '__main__':
    schedule_init()
