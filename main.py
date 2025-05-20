import os
import datetime
from bookings_tracker import *
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

date_arr = schedule_check()
if os.getenv("DATES"):
	date_arr = check_dates(os.getenv("DATES").split(','))
	
#Iterate through missing
#Scrape online tables for each date
if date_arr:
	result_arr = []
	for day in date_arr:
		result_arr.append(Booking(day))
	
	#write_to_all(result_arr)
	failed_dates = []
	for booking in result_arr:
		if not booking.success:
			failed_dates.append(booking.formatted_date)
	if failed_dates: print('Scraping failed for ' + ', '.join(failed_dates))
	push_note()