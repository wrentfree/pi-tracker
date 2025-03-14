import os
import datetime
import copy
from coptracker import table_scrape
from local import write_to_local
from heroku import write_to_heroku
from drive import write_to_drive
from check import check

#TODO: provide way to force run certain dates

#Check schedule to find dates that failed, will include today's initiated date
#Returns [(date, local_success, heroku_success, drive_success)] in list of tuples

missing_arr = check()
date_arr = []
if os.getenv("DATES"):
	date_arr = os.getenv("DATES").split(',')
else:
	for d in missing_arr:
		date_arr.append(d[0].strftime("%m/%d/%Y"))

#Iterate through missing
#Scrape online tables for each date

print(date_arr)
if date_arr:
	results = table_scrape(date_arr)
	print(results)

	#write_to_local(date_arr, copy.deepcopy(results))
	#write_to_heroku(date_arr, copy.deepcopy(results))
	#write_to_drive(date_arr, copy.deepcopy(results))

