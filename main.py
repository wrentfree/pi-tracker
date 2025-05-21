import os
import datetime
from bookings_tracker import *
from write_results import *
from schedule_methods import *
from push_notifications import push_note

# This is the main script that runs daily in order to collect and record
# all data for any days missing data, starting with two days ago

# The reason we start two days ago is due to the booking process.
# Booking data can sometimes change or be added to up to a day later.

# Check schedule to find dates that failed, will include today's initiated date
# Returns [(date, local_success, heroku_success, drive_success)] in list of tuples
schedule_init()

date_arr = []
for row in schedule_check():
	date_arr.append(row['date'])

# If present, format DATES environment variable
if os.getenv("DATES"):
	date_arr = check_dates(os.getenv("DATES").split(','))
	
#Iterate through missing
#Scrape online tables for each date
if date_arr:
	drive_arr = []
	local_arr = []
	heroku_arr = []
	all_arr = []
	for day in date_arr:
		booking = Booking(day)
		schedule = Schedule(day)
		all_arr.append(booking)
		if not schedule.local_success:
			local_arr.append(booking)
		if not schedule.heroku_success:
			heroku_arr.append(booking)
		if not schedule.drive_success:
			drive_arr.append(booking)
	
	write_to_local(local_arr)
	write_to_heroku(heroku_arr)
	write_to_drive(drive_arr)

	failed_dates = []
	for booking in all_arr:
		if not booking.success:
			failed_dates.append(booking.formatted_date)
	if failed_dates: print('Scraping failed for ' + ', '.join(failed_dates))
	push_note()