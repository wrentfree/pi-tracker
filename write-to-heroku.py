import csv
import psycopg2
import os
import datetime
from coptracker import table_scrape, execute_queries

conn = psycopg2.connect('host=ec2-44-213-151-75.compute-1.amazonaws.com user=ehzrohbdkkzvno password=2d510648de5837e946151984d4abfa9264a9ab35f075276d66cf3a18f1b02d74 dbname=d2c3huobn2rnjq')
cur = conn.cursor()

results = table_scrape()
execute_queries(results['queries'], 'heroku', conn, cur)
print('\nEntries written to keroku')

