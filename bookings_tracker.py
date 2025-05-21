#!/usr/bin/env python

from datetime import date
from datetime import timedelta
from drive_methods import *
from address_parse import *
import csv
import psycopg2
import os
import datetime
import requests
import uncurl

today = date.today()
today_string = today.strftime('%b-%d-%Y')

class Booking:
    """This class handles booking data for a specific date

    Parameters
    ----------
    date_object : datetime.date
        The date to be queried for booking data
    
    Attributes
    ----------
    date_object : date
        The date object initially passed
    formatted_date : str
        The date reformatted as a string
    csv_title : str
        Formatted CSV title
    success : bool
        Whether the API request was retrieved and formatted successfully
    json_response: json
        JSON body of API response
    formatted_response : [dict]
        JSON response formatted as a list of dictionaries
            'Police Id'
            'Name'
            'Address'
            'Street Address'
            'City'
            'Zipcode'
            'Age at Arrest'
            'Arresting Agency'
            'Charges'
    queries : [str]
        List of postgreSQL queries for updating dbs
    
    Methods
    -------

    """

    def __init__(self, date_object):
        self.date_object = date_object
        self.formatted_date = date_object.strftime('%Y-%m-%d')
        self.csv_title = date_object.strftime('%b-%d-%Y') + '.csv'
        self.success = True
        self.json_response = self.api_request(date_object)
        self.formatted_response = []
        if self.success and self.json_response: self._format_response()
        self.queries = []
        if self.success and self.formatted_response:
            for row in self.formatted_response:
                self._format_query(row)
    
    def api_request(self, date_object):
        try:
            day = self.formatted_date
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
            return r.text
        except Exception as e:
            print('Issue making api request')
            print(e)
            self.success = False
    
    def _format_response(self):
        try:
            json_data = json.loads(self.json_response)
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
                self.formatted_response.append({'Police Id': police_id, 'Name': name, 'Address': address, 'Street Address': street_addr,
                                'City': city, 'Zipcode': zipcode, 'Age at Arrest': age,
                                'Arresting Agency': agency, 'Charges': charges})
        except Exception as e:
            print('Issue parsing json body')
            self.success = False
            print(e)
    
    def _format_query(self, row):
        date = self.date_object.strftime('%m/%d/%Y')
        police_id = row['Police Id']
        name = row['Name']
        address = row['Address']
        street_address = row['Street Address']
        city = row['City']
        zipcode = row['Zipcode']
        age = row['Age at Arrest']
        agency = row['Arresting Agency']
        charges = row['Charges']

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
        self.queries.append(new_string)
    
    def write_csv(self):
        with open(self.csv_title, 'w', newline='') as csvfile:
            fieldnames = ['Police Id', 'Name', 'Address', 'Street Address', 'City', 'Zipcode',
                          'Age at Arrest', 'Arresting Agency', 'Charges']
            wr = csv.DictWriter(csvfile, fieldnames=fieldnames)
            wr.writeheader()
            for row in self.formatted_response:
                wr.writerow(row)
