#!/usr/bin/env python

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from Screenshot import Screenshot
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
screenshot_string = today.strftime('%b-%d-%Y %H:%M:%S') + '.png'
print(today_string + ' Starting ...')
ob = Screenshot.Screenshot()
display = Display(visible=0, size=(1600, 1200))
display.start()
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', \
                          options=chrome_options)
print('webdriver loaded')

def check_dates(dates=[]):
    env_dates = []
    if os.getenv('DATES') == ['all']:
         env_dates = 'all'
    elif os.getenv('DATES'):
        env_dates = os.getenv('DATES').split(',')
        format_dates = []
        for date_info in env_dates:
            format_dates.append(datetime.datetime.strptime(date_info, '%m/%d/%Y'))
        env_dates = format_dates
    elif len(dates) > 0:
        format_dates = []
        for date_info in dates:
            if type(date_info) is str:
                format_dates.append(datetime.datetime.strptime(date_info, '%m/%d/%Y'))
            elif type(date_info) is datetime.datetime:
                format_dates.append(date_info)
        env_dates = format_dates
    else:
        env_dates = [today]
    return env_dates

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

def format_dates(dates):
    dates_info = []
    
    if dates == 'all':
        i = 29
        while i >= 0:
            date_info = today - timedelta(days = i)
            dates_info.append({'date_info': date_info,
                                'url': 'http://www.hcsheriff.gov/cor/display.php?day=' + str(i),
                                'csv': date_info.strftime('%b-%d-%Y') + '.csv'})
            i = i-1
    else:
        for date_info in dates:
            today_dt = datetime.datetime.combine(today, datetime.datetime.min.time())
            date_dt = datetime.datetime.combine(date_info, datetime.datetime.min.time())
            url_num = (today_dt - date_dt).days
            dates_info.append({'date_info': date_info,
                               'url': 'http://www.hcsheriff.gov/cor/display.php?day=' + str(url_num),
                               'csv': date_info.strftime('%b-%d-%Y') + '.csv'})
   
    return dates_info
    
    

# Scrapes the previous day's booking table, returns csv name.
def table_scrape(dates):
    query_list = []
    csv_list = []
    dates = check_dates(dates)
    dates_info = format_dates(dates)
    for info in dates_info:
        date_info = info['date_info']
        url = info['url']
        csv_title = info['csv']
        csv_list.append(csv_title)
        print('Scraping ' + csv_title)
        
        try:
            driver.get(url)
            Wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'booking_reports_list')))
            table = driver.find_element(By.CLASS_NAME, 'booking_reports_list')
        except Exception as e:
            file_name = today_string
            ob.full_Screenshot(driver, save_path=r'./screenshots', image_name=screenshot_string)
            raise e
        
        # Writes the table to a csv named after yesterday's date
        with open(csv_title, 'w', newline='') as csvfile:
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
                    query = get_query_string(date_info.strftime('%m/%d/%Y'),\
                                     name, address, street_addr, city, zipcode, age, agency, charges)
                    query_list.append(query)
       
    print('Done')
    driver.quit()
    return {'queries': query_list, 'dates_info': dates_info}


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
