#!/usr/bin/env python

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
from datetime import timedelta
from drive_upload import *
from address_parse import *
import csv

# Returns an array of all created csv's
def scrape_all_tables():
    print('Starting ...')
    display = Display(visible=0, size=(1600, 1200))
    display.start()
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', \
                              options=chrome_options)
    print('webdriver loaded')

    # Navigate to target website
    file_name_arr = []
    count = 29
    while count >= 0:
        driver.get('http://www.hcsheriff.gov/cor/display.php?day=' + str(count))

        table = driver.find_element(By.CLASS_NAME, 'booking_reports_list')

        # Use yesterday's date as the title of the csv
        today = date.today()
        yesterday = today - timedelta(days = count)
        yesterdayString = yesterday.strftime('%b-%d-%Y')

        # Writes the table to a csv named after yesterday's date
        with open(yesterdayString + '.csv', 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Address', 'Street Address', 'City', 'Zipcode',
                          'Age at Arrest', 'Arresting Agency', 'Charges']
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
                
                    # Format address
                    address = rowtextarr[1].strip()
                    zip_arr = zip_coder(address)
                    # Add state to address to improve parsing
                    space_index = address.rfind(' ')
                    address = address[:space_index] + ' ' + zip_arr[2] + address[space_index:]
                    # Add state even if zip code is missing to help with parsing
                    if len(zip_arr[1]) == 0:
                        address += ' TN'
                    street_addr_arr = address_parser(address)
                    
                    # Address values
                    street_addr = street_addr_arr[0]
                    city = zip_arr[0]
                    zipcode = zip_arr[1]
                    
                    # Format all other info
                    name = rowtextarr[0]
                    age = rowtextarr[2][15:17]
                    agency = rowtextarr[3][18:]
                    
                    # Write row in csv file
                    wr.writerow({'Name': name, 'Address': address, 'Street Address': street_addr,
                                 'City': city, 'Zipcode': zipcode, 'Age at Arrest': age,
                                 'Arresting Agency': agency, 'Charges': charges})
           
        print('Done ' + str(count))
        file_name_arr.append(yesterdayString + '.csv')
        count = count - 1
    driver.quit()
    return file_name_arr

# given an array of file names, will upload to Bookings folder
def upload_all(file_array):
    for file in file_array:
        upload_to_folder(real_folder_id='1z_QtU4t1iaAOowzpQPfyv2iKEGnKh9ND', \
                         file_name=file, \
                         file_type="text/csv")
        print(file + ' uploaded')
    print('All files uploaded')

# Scrape table, create files
booking_files = scrape_all_tables()
# Upload all files to Drive
upload_all(booking_files)