import psycopg2
import os
import datetime
from datetime import date

#Returns [(date, local_success, heroku_success, drive_success)] in list of
#tuples
def check():
	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()

	today_string = date.today().strftime('%m/%d/%Y')
	query = "SELECT date, local_success, heroku_success, drive_success FROM schedule WHERE local_success = FALSE OR heroku_success = FALSE OR drive_success = FALSE"
	cur.execute(query)
	response = cur.fetchall()

	conn.close()
	cur.close()
	return response
