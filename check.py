import psycopg2
import os
import datetime
from datetime import date
import json

connection_string = ''

with open('config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostrgres']

#Returns [(date, local_success, heroku_success, drive_success)] in list of
#tuples
def check():
	conn = psycopg2.connect(connection_string)
	cur = conn.cursor()

	today_string = date.today().strftime('%m/%d/%Y')
	query = "SELECT date, local_success, heroku_success, drive_success FROM schedule WHERE local_success = FALSE OR heroku_success = FALSE OR drive_success = FALSE"
	cur.execute(query)
	response = cur.fetchall()

	conn.close()
	cur.close()
	return response
