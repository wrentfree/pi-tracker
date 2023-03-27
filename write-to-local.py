import csv
import psycopg2
import os
import datetime
from coptracker import table_scrape, execute_queries

conn = psycopg2.connect('host=192.168.68.59 user=postgres password=Postgress dbname=bookings')
cur = conn.cursor()

results = table_scrape()
execute_queries(results['queries'], 'local', conn, cur)
print('\nEntries written to local')
