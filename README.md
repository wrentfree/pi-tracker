# pi-tracker
selenium project on raspberry pi

## Configuration

You can use `sudo apt-get install chromium-chromedriver` to get the latest chromedriver compatible with chromium for raspberry pi

Other dependencies:
```
sudo apt-get install xvfb
sudo pip install PyVirtualDisplay
sudo pip install xvfbwrapper
sudo pip install psycopg2
sudo pip install psycopg2
```
Pillow, usaddress, uszipcode are additional libraries used, but I am unsure
if I used pip.

## Scripts

The script that runs daily is  `index.py`.
It will query the schedule PSQL table to find all dates with missing uploads
and will itterate through the dates to ensure every db has complete data.
