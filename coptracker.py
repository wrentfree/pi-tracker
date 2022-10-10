#!/usr/bin/env python

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
from datetime import timedelta
from drive_upload import *
import csv


today = date.today()
today_string = today.strftime('%b-%d-%Y')
print(today_string + ' Starting ...')
display = Display(visible=0, size=(1600, 1200))
display.start()
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', \
                          options=chrome_options)
print('webdriver loaded')

# Scrapes the previous day's booking table, returns csv name.
def table_scrape():
    # Navigate to target website
    driver.get('http://www.hcsheriff.gov/cor/display.php?day=1')

    table = driver.find_element(By.CLASS_NAME, 'booking_reports_list')

    # Use yesterday's date as the title of the csv
    yesterday = today - timedelta(days = 1)
    yesterdayString = yesterday.strftime('%b-%d-%Y')

    # Writes the table to a csv named after yesterday's date
    with open(yesterdayString + '.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Address', 'Age at Arrest', 'Arresting Agency', 'Charges']
        wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
        wr.writeheader()
        
        # parses the rows
        for row in table.find_elements(By.CSS_SELECTOR, 'tr'):
            rowtext = [d.text for d in row.find_elements(By.CSS_SELECTOR, 'td')]
            rowtextarr = rowtext[0].split('\n')
            
            # Collects the list of charges
            ch = [d.text for d in row.find_elements(By.CSS_SELECTOR, 'ul')]
            
            
            if 'Booking Report Date' in rowtextarr[0]:
                continue
            else:
                # Format charges
                charges = ch[0].replace('\n', ', ')
                
                # Format all other info
                name = rowtextarr[0]
                address = rowtextarr[1]
                age = rowtextarr[2][15:17]
                agency = rowtextarr[3][18:]
                
                # Write row in csv file
                wr.writerow({'Name': name, 'Address': address, 'Age at Arrest': age, \
                              'Arresting Agency': agency, 'Charges': charges})
       
    print('Done')
    print('')
    driver.quit()
    return yesterdayString + '.csv'

# Uploads file to drive
def upload_to_drive(csv_name):
    pass

file_name = table_scrape()
upload_to_folder(real_folder_id='1z_QtU4t1iaAOowzpQPfyv2iKEGnKh9ND', \
                 file_name=file_name, \
                 file_type="text/csv")