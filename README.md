# pi-tracker
selenium project on raspberry pi

****Configuration****

You can use `sudo apt-get install chromium-chromedriver` to get the latest chromedriver compatible with chromium for raspberry pi

Other dependencies:
```
sudo apt-get install xvfb
sudo pip install PyVirtualDisplay
sudo pip install xvfbwrapper
```

*Scripts*

`coptracker.py` is the script that runs daily that scrapes the Hamilton County Sheriff's Office booking table from the previous day and saves it as a csv.

'coptracker_backlog.py' will cycle through all available tables except the previous day's.
