# pi-tracker
A webscraper project created for CALEB, a Chattanooga nonprofit, for the purpose of obtaining and retaining publicly available booking
data for the purpose of critical data analysis of the people and areas most affected by police in Hamilton County.

You can find the reports [here](https://www.calebcha.org/pretrial-report.html).

## Configuration

The first iteration of this project used Selenium to obtain information from the Hamilton County Sheriff's Office website, but due to changes they have made to their site,
the much quicker approach of making an API request is now the main method of obtaining data.

Other dependencies:
```
sudo apt-get install xvfb
sudo pip install PyVirtualDisplay
sudo pip install xvfbwrapper
sudo pip install psycopg2
```
Pillow, usaddress, uszipcode, uncurl, google modules, and possibly a few others are additional libraries used and installed via pip. You may have to run the program to see if any additional 
libraries are missing.

### Google API

You will need to follow Google's Developer instructions if you would like to create copies of the reports in your drive by copying the `token.json.example` and `credentials.json.example` files and filling in your personal information there.

### Postgres
If you would like to record the information in a PostgreSQL database, you will need to set them up yourself, then fill the information into a copy of the `config.json.example` file. I have not yet created a script for the intial creation of the relative tables.

### Pushbullet
If you would like updates pushed to your phone, you will have to configure the `config.json.example` file.

## Scripts

The script that runs daily using crontab is  `index.py`.
It will query the schedule PSQL table to find all dates with missing uploads
and will itterate through the dates to ensure every db has complete data.
