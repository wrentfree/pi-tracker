#!/usr/bin/env python

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
import requests
import uncurl

today = date.today()
today_string = today.strftime('%b-%d-%Y')
screenshot_string = today.strftime('%b-%d-%Y %H:%M:%S') + '.png'
print(today_string + ' Starting ...')
ob = Screenshot.Screenshot()

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

# After changes made to the hamilton county website, we are no longer able to navigate by url and must update the value of an element instead.
# Format dates will now keep an array of dates in the format of "Wed Mar 12 2025 09:26:58 GMT-0400 (Eastern Daylight Time)"
def format_dates(dates):
    dates_info = []
    for date_info in dates:
        today_dt = datetime.datetime.combine(today, datetime.datetime.min.time())
        date_dt = datetime.datetime.combine(date_info, datetime.datetime.min.time())
        url_num = (today_dt - date_dt).days
        dates_info.append({'date_info': date_info,
                           'formatted_date': date_info.strftime('%Y-%m-%d'),
                           'csv': date_info.strftime('%b-%d-%Y') + '.csv'})
   
    return dates_info
    
    

# Scrapes the previous day's booking table, returns csv name.
# After website change, dates_info() now returns an array of [date_info, formatted_date, csv]
def table_scrape(dates):
    query_list = []
    csv_list = []
    dates = check_dates(dates)
    dates_info = format_dates(dates)
    for info in dates_info:
        date_info = info['date_info']
        # Changed "url" variable to "day"
        day = info['formatted_date']
        csv_title = info['csv']
        csv_list.append(csv_title)
        print('Scraping ' + csv_title)
        
        #Get information using curl bash
        try:
            curl_string = ("""curl 'https://hcsheriff.gov/Corrections/api' \
              -H 'accept: */*' \
              -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
              -H 'content-type: text/plain;charset=UTF-8' \
              -H 'origin: https://hcsheriff.gov' \
              -H 'priority: u=1, i' \
              -H 'referer: https://hcsheriff.gov/Corrections/Booking-app' \
              -H 'sec-ch-ua: "Not/A)Brand";v="8", "Chromium";v="126"' \
              -H 'sec-ch-ua-mobile: ?0' \
              -H 'sec-ch-ua-platform: "Linux"' \
              -H 'sec-fetch-dest: empty' \
              -H 'sec-fetch-mode: cors' \
              -H 'sec-fetch-site: same-origin' \
              -H 'user-agent: Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
              --data-raw '{}'""".format('{"date":"'+day+'"}'))
            ctx = uncurl.parse_context(curl_string)
            r = requests.request(ctx.method.upper(), ctx.url, data=ctx.data, cookies=ctx.cookies, headers=ctx.headers, auth=ctx.auth)
            print(r)
            data = r.text
            print(data)
        except Exception as e:
            print('Issue making api request')
            raise e

        # Needs to be converted to parse API response
        # parses the rows
        try:
            json_data = json.loads(data)
            rows = table.find_elements(By.CSS_SELECTOR, 'li')
            if len(rows) == 0:
                raise('No rows found')
            for row in rows:
                rowtext = [d.text for d in row.find_elements(By.CSS_SELECTOR, 'div')]
                print('entries')
                print(rowtext)
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
        except Exception as e:
            print('Issue parsing addresses from table')
            #driver.quit()
            raise e     
            
        # Writes the table to a csv named after yesterday's date
        with open(csv_title, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Address', 'Street Address', 'City', 'Zipcode',
                          'Age at Arrest', 'Arresting Agency', 'Charges']
            wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
            wr.writeheader()
    print('Done')
    #driver.quit()
    return {'queries': query_list, 'dates_info': dates_info}
