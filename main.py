import os
import datetime
from bookings_tracker import table_scrape
from write_results import write_to_all
from schedule_methods import *
from push_notifications import push_note

# This is the main script that runs daily in order to collect and record
# all data for any days missing data, starting with two days ago

# The reason we start two days ago is due to the booking process.
# Booking data can sometimes change or be added to up to a day later.

#Check schedule to find dates that failed, will include today's initiated date
#Returns [(date, local_success, heroku_success, drive_success)] in list of tuples
schedule_init()

missing_arr = schedule_check()
date_arr = []
if os.getenv("DATES"):
	date_arr = os.getenv("DATES").split(',')
else:
	for d in missing_arr:
		date_arr.append(d[0].strftime("%m/%d/%Y"))

# Reformat date strings into date objects
date_arr = check_dates(date_arr)
	
#Iterate through missing
#Scrape online tables for each date

print(date_arr)
if date_arr:
	results = table_scrape(date_arr)
	#print(results)
	
	# results is [{date_info: Date object,
	#			  formatted_date: date string,
	#             csv: csv title string,
	#			  success: boolean for successful scrape for that date,
	#			  queries: ["list of query strings"]}]
	#write_to_all(results)
	failed_dates = []
	for result in results:
		if not result['success']:
			failed_dates.append(result['formatted_date'])
	if failed_dates: print('Scraping failed for ' + ', '.join(failed_dates))
	push_note()