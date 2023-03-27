#!/usr/bin/env python

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
from datetime import timedelta
from drive_upload import *
from booking_folder_maker import *
from address_parse import *
import csv
import psycopg2
import os
import datetime


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

def get_query_string(date, name, address, street_address, city, zipcode, age, agency, charges):
    if not date:
        date = 'NULL'
    if not name:
        name = 'NULL'
    if not address:
        address = 'NULL'
    if not street_address:
        street_address = 'NULL'
    if not city:
        city = 'NULL'
    if not zipcode:
        zipcode = 'NULL'
    if not age:
        age = 'NULL'
    if not agency:
        agency = 'NULL'
    if not charges:
        charges = 'NULL'
    
    name = name.replace("'", "''")
    address = address.replace("'", "''")
    street_address = street_address.replace("'", "''")
    city = city.replace("'", "''")
    agency = agency.replace("'", "''")
    charges = charges.replace("'", "''")
    
    query_string = ("""INSERT INTO bookings
(date, name, address, street_address, city, zipcode, age_at_arrest, arresting_agency, charges)
VALUES(
'{}',
'{}',
'{}',
'{}',
'{}',
{},
{},
'{}',
'{}');""".format(date, name, address, street_address, city, zipcode, age, agency, charges))
    new_string = query_string.replace("'NULL'", "NULL")
    return(new_string)

def execute_queries(queries, db, conn, cur):
    for query in queries:
        try:
            cur.execute(query)
        except psycopg2.errors.InFailedSqlTransaction:
            print(db + ' transaction rolled back')
            print(query)
            conn.rollback()
        except Exception as e:
            print(db + ' query failed')
            print(query)
            print(type(e))
            print(e)
        else:
            conn.commit()

def write_to_local_db(queries, conn, cur):
    # conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
    # cur = conn.cursor()
    execute_queries(queries, 'local', conn, cur)
    conn.close()

def write_to_heroku_db(queries, conn, cur):
    # conn = psycopg2.connect('host=ec2-44-213-151-75.compute-1.amazonaws.com user=ehzrohbdkkzvno password=2d510648de5837e946151984d4abfa9264a9ab35f075276d66cf3a18f1b02d74 dbname=d2c3huobn2rnjq')
    # cur = conn.cursor()
    execute_queries(queries, 'heroku', conn, cur)
    conn.close()
    cur.close()

def heroku_test():
    conn = psycopg2.connect('host=ec2-44-213-151-75.compute-1.amazonaws.com user=ehzrohbdkkzvno password=2d510648de5837e946151984d4abfa9264a9ab35f075276d66cf3a18f1b02d74 dbname=d2c3huobn2rnjq')
    cur = conn.cursor()
    cur.execute('SELECT * FROM bookings ORDER BY date DESC LIMIT 10;')

# Scrapes the previous day's booking table, returns csv name.
def table_scrape():
    query_list = []
    # Navigate to target website
    driver.get('http://www.hcsheriff.gov/cor/display.php?day=2')

    table = driver.find_element(By.CLASS_NAME, 'booking_reports_list')

    # Use yesterday's date as the title of the csv
    yesterday = today - timedelta(days = 2)
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
                address_to_parse = address[:space_index] + ' ' + zip_arr[2] + address[space_index:]
                # Add state even if zip code is missing to help with parsing
                if len(zip_arr[1]) == 0:
                    address_to_parse = address + ' TN'
                street_addr_arr = address_parser(address_to_parse)
                if ''.join(street_addr_arr) == "TN":
                    street_addr_arr = ["Address not listed", "", ""]
                
                # Address values
                street_addr = street_addr_arr[0]
                city = zip_arr[0]
                zipcode = zip_arr[1]
                
                # Backup values if zipcode parser fails due to bad zip code
                if len(city) == 0:
                    city = street_addr_arr[1]
                
                # Format all other info
                name = rowtextarr[0]
                age = rowtextarr[2][15:17]
                agency = rowtextarr[3][18:]
                
                # Write row in csv file
                wr.writerow({'Name': name, 'Address': address, 'Street Address': street_addr,
                             'City': city, 'Zipcode': zipcode, 'Age at Arrest': age,
                             'Arresting Agency': agency, 'Charges': charges})
                
                # Write row to db
                query = get_query_string(datetime.datetime.strptime(yesterdayString, '%b-%d-%Y').strftime('%m/%d/%Y'),\
                                 name, address, street_addr, city, zipcode, age, agency, charges)
                query_list.append(query)
       
    print('Done')
    driver.quit()
    return {'csv_title': yesterdayString + '.csv', 'queries': query_list}

"""
results = table_scrape()
file_name = results['csv_title']
queries = results['queries']

# Commit to DB


try:
    write_to_local_db(queries)
except Exception as e:
    print('failed to write to local db')
    print(e)
else:
    print('Written to local db')


#heroku_test()
write_to_heroku_db(queries)
        

# If folder exists and is in the 'Bookings' folder, upload file to folder
# else create folder in the 'Bookings' folder and upload file to folder
folder_id = get_folder(folder_name)
upload_to_folder(real_folder_id=folder_id, \
                 file_name=file_name, \
                 file_type="text/csv")
"""
