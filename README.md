# pi-tracker
A webscraper project created for CALEB, a Chattanooga nonprofit, for the purpose of obtaining and retaining publicly available booking
data for the purpose of critical data analysis of the people and areas most affected by police in Hamilton County.

You can find the reports on CALEB's [website](https://www.calebcha.org/pretrial-report.html) and local news coverage [here](https://www.wdef.com/report-says-most-hamilton-county-inmates-stay-behind-bars-through-the-end-of-their-case/).

## Configuration

The first iteration of this project used Selenium to obtain information from the Hamilton County Sheriff's Office website, but due to changes they have made to their site,
the much quicker approach of making an API request is now the main method of obtaining data.

Other dependencies:
```
pip --user install usaddress uszipcode psycopg2 uncurl pushbullet.py
pip --user install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Google API

You will need to follow Google's Developer [instructions](https://developers.google.com/workspace/drive/api/quickstart/python) if you would like to create copies of the reports in your Google Drive. Once you create a client id, download the client secret, add it to the project directory, and rename it to `credentials.json`.
Once the file is added, run `drive_quickstart.py`, follow the instructions on your browser, and it will generate your new `token.json` file.
You will only have to do this once and if you wish, you may remove `drive_quickstart.py` and `credentials.json` afterwards.

### Postgres
Install postgres on your computer then use the `table_creation.sql` script to create local tables.
You can also use this script to create a remote copy of the `bookings` table.
```
psql -U your-username -c 'create database bookings;'
psql -U your-username -d bookings -a -f table_creation.sql
```
This creates a database named bookings with two tables: `bookings` and `schedule`.

### Pushbullet
If you would like updates pushed to your phone, you will have to configure the `config.json.example` file.

## Scripts

Using crontab, I've created a series of executions that
1. Run the 'schedule-methods.py` file which creates a row in a PostgreSQL table for tracking script completion successes.
2. Run the `main.py` file containing the scripts to be run and updates the script completion table.
3. Run `push-notification.py` which queries the script completion table and sends me a push notification on my phone reporting script success or failure.

It's important to note that `main.py` will not function properly without first running `schedule_methods.py`
