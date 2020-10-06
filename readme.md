A simple Python script to find the current temperature using the OpenWeatherMap API. Prompt supports U.S. states in both long and short form.\
You will need to provide your own API Key in the .env file.

Output from weather_grabbery.py -h\
usage: weather_grabber.py [-h] [--city CITY] [--state STATE] [--lang LANG]
                          [--units {imperial,metric,standard}] [--version]

Get the current weather from a specified location through the OpenWeatherMap API.

optional arguments:\
  -h, --help            show this help message and exit\
  --city CITY           any city worldwide\
  --state STATE         US state of entered city\
  --lang LANG           abbreviated language code\
  --units {imperial,metric,standard} choose between Fahrenheit, Celsius, or Kelvin units\
  --version             show program's version number and exit\

