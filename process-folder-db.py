# This file is used for migrating data from csv files to Postgres dbs, used once near the beginning of the project once dbs were implemented.

import datetime
import psycopg2
import csv
import os
import json

connection_string = ''
directory = '/home/wren/Desktop/Bookings/Bookings Mar-2023'

with open('config.json') as f:
    json_data = json.load(f)
    connection_string = json_data['localPostrgres']

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

# Import data from csv

# Get file names to pass into csv reader

def get_all_files(directory):
    file_names = os.listdir(directory)
    all_data = []
    for file_name in file_names:
        # Retrieve only csv files
        if '.csv' in file_name:
            with open('{}/{}'.format(directory, file_name), newline='') as csvfile:
                print('{}/{}'.format(directory, file_name))
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                # Parse data (skips first line which is title row)
                iterrows = iter(csv_reader)
                next(iterrows)
                for row in iterrows:
                    file_data = {'date': datetime.datetime.strptime(file_name.split('.')[0], '%b-%d-%Y').strftime('%m/%d/%Y'),
                                 'name': row[0],
                                 'address': row[1],
                                 'street_address': row[2],
                                 'city': row[3],
                                 'zipcode': row[4],
                                 'age': row[5],
                                 'agency': row[6],
                                 'charges': row[7]}
                    all_data.append(file_data)
    return all_data

def create_queries(data_list):
    queries = []
    for row in data_list:
        if row is not None:
            queries.append(get_query_string(row['date'],\
                                            row['name'],\
                                            row['address'],\
                                            row['street_address'],\
                                            row['city'],\
                                            row['zipcode'],\
                                            row['age'],\
                                            row['agency'],\
                                            row['charges']))
    return queries

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

def execute_queries(queries):
    for query in queries:
        cur.execute(query)
        
def query_table():
    cur.execute("SELECT * FROM bookings;")
    responses = cur.fetchall()
    for response in responses:
        print(response)

data = get_all_files(directory)
queries = create_queries(data)
execute_queries(queries)
query_table()

conn.commit()

