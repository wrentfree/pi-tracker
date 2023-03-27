from coptracker import *
import datetime
import os

today = datetime.datetime.now()
delta = datetime.timedelta(days = 2)
date = today - delta
env_dates = [date]
if os.getenv('DATES'):
	env_dates = os.getenv('DATES').split(',')

# If folder exists and is in the 'Bookings' folder, upload file to folder
# else create folder in the 'Bookings' folder and upload file to folder
table_info = table_scrape(env_dates)

dates_info = table_info['dates_info']

for day_info in dates_info:
	print(day_info)
	folder_id = get_folder('Bookings ' + day_info['date_info'].strftime('%b-%Y'))
	file_name = day_info['csv']
	upload_to_folder(real_folder_id=folder_id, file_name=file_name, file_type="text/csv")

if os.getenv('SCHEDULE').lower() == 'true':
	conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
	cur = conn.cursor()
	query = "UPDATE schedule SET drive_success = TRUE WHERE date = '{}';".format(today.strftime('%m/%d/%Y'))
	cur.execute(query)
	conn.commit()
	conn.close()
	cur.close()
