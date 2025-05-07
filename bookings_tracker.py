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

def get_query_string(date, police_id, name, address, street_address, city, zipcode, age, agency, charges):
    if not date:
        date = 'NULL'
    if not police_id:
        police_id = 'NULL'
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
(date, police_id, name, address, street_address, city, zipcode, age_at_arrest, arresting_agency, charges)
VALUES(
'{}',
'{}',
'{}',
'{}',
'{}',
'{}',
{},
{},
'{}',
'{}');""".format(date, police_id, name, address, street_address, city, zipcode, age, agency, charges))
    new_string = query_string.replace("'NULL'", "NULL")
    return(new_string)

def execute_queries(queries, db, conn, cur):
    for query in queries:
        try:
            cur.execute(query)
        except psycopg2.errors.InFailedSqlTransaction as e:
            print(db + ' transaction rolled back likely due to duplicate')
            print(query)
            print(type(e))
            print(e)
            print('')
            #conn.rollback()
        except Exception as e:
            print(db + ' query failed')
            print(query)
            print(type(e))
            print(e)
            print('')
            #conn.rollback()
        else:
            #conn.commit()
            #print('autocommited')

def format_dates(dates):
    dates_info = []
    for date_info in dates:
        dates_info.append({ 'date_info': date_info,
                            'formatted_date': date_info.strftime('%Y-%m-%d'),
                            'csv': date_info.strftime('%b-%d-%Y') + '.csv',
                            ,'success': True,'queries': []})
    return dates_info

# Scrapes the previous day's booking table, returns csv name.
# After website change, dates_info() now returns a dictionary of
# {date_info, formatted_date, csv, success, queries}
def table_scrape(dates):
    dates = check_dates(dates)
    dates_info = format_dates(dates)
    for info in dates_info:
        date_info = info['date_info']
        # Changed "url" variable to "day"
        day = info['formatted_date']
        csv_title = info['csv']
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
            # print(r)
            data = r.text
            #print(data)
        except Exception as e:
            print('Issue making api request')
            raise e

        # Needs to be converted to parse API response
        # parses the rows
        """
        {"R_ID":"CA1A324A-ADFC-4024-BD9B-10A74A9DF36D","Verified":0,"Name":"Oscar Grouch",
        "AddressStreet":"123 SESAME STREET","AddressCity":"CHATTANOOGA","AddressZip":"37423",
        "HML_AGE_AT_ARREST":4,"HML_ARREST_AGENCY":"HC Sheriff","HML_COMMITTAL_DATE":"2025-04-01T00:00:00.000Z",
        "HML_COMMITTAL_TIME":"3 :35","DT_Created":"2025-04-01T10:08:56.740Z",
        "PrtOffense1":"TOO GROUCHY","PrtOffense2":"","PrtOffense3":"
        """
        # It also appears that sometimes a person will be booked twice.
        # To prevent confusion, I've decided to also include the "R_ID"
        # property in the API response and revise the UNIQUE constraints
        # on the bookings PSQL table.
        # Writes the table to a csv named after yesterday's date
        with open(csv_title, 'w', newline='') as csvfile:
            fieldnames = ['Police Id', 'Name', 'Address', 'Street Address', 'City', 'Zipcode',
                          'Age at Arrest', 'Arresting Agency', 'Charges']
            wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
            wr.writeheader()
            try:
                json_data = json.loads(data)
                if len(json_data['body']) == 0:
                    raise('No rows found')
                for row in json_data['body']:
                    # Collects the list of charges
                    charges = ''
                    i = 1
                    while i <= 48:
                        key = 'PrtOffense' + str(i)
                        if not row[key]:
                            break
                        if i == 1:
                            charges = charges + row[key]
                        else:
                            charges = charges + ',' + row[key]
                        i+=1
                    #print(charges)
                    
                    
                    
                    # Format address
                    street_addr = row['AddressStreet']
                    city = row['AddressCity']
                    zipcode = row['AddressZip']
                    address = (street_addr + ' ' + city + ' ' + zipcode).strip()
                    
                    if not city:
                        city = zip_coder(zipcode)[0]
                    if 'homeless' in address.lower():
                        street_addr = 'HOMELESS'
                    
                    # Format all other info
                    name = row['Name']
                    age = row['HML_AGE_AT_ARREST']
                    agency = row['HML_ARREST_AGENCY']
                    police_id = row['R_ID']
                    
                    # Write row in csv file
                    wr.writerow({'Police Id': police_id, 'Name': name, 'Address': address, 'Street Address': street_addr,
                                    'City': city, 'Zipcode': zipcode, 'Age at Arrest': age,
                                    'Arresting Agency': agency, 'Charges': charges})
                    
                    # Write row to db
                    info['queries'].append(get_query_string(date_info.strftime('%m/%d/%Y'),\
                                        police_id, name, address, street_addr,\
                                        city, zipcode, age, agency, charges))
            except Exception as e:
                print('Issue parsing json body')
                #driver.quit()
                #Continue to next day
                info['success'] = False
                print(e)
            finally
                continue

    print('Done')
    return dates_info
