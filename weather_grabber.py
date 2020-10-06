import argparse
import csv
import os
import pprint
import re

import requests
from dotenv import load_dotenv

load_dotenv()
DEFAULT_API_KEY = os.getenv('API_APP_ID')
DEFAULT_API_ENDPOINT = os.getenv('API_ENDPOINT')
DEFAULT_API_LANG = os.getenv('API_LANG')
DEFAULT_LINE_LENGTH = os.getenv('LINE_LENGTH')
VER_NO = os.getenv('VERSION_NUMBER')


# Get input from the user
def get_location_from_user():
    user_input = 'Des Moines IA'
    #user_input = input('Where are you? (City, State)\n')
    out = re.search('([A-Za-z]+(?: ?[A-Za-z]+)),? ?([A-Za-z]+(?: ?[A-Za-z])+)*$', user_input)
    print(out[1])
    print(out[2])

    # city_raw = input_split[0]
    # state_raw = input_split[1]
    # state = format_us_state(state_raw)
    # location = f'{city_raw},{state}'
    # location = 'New York,US-NY'
    # return location


# Convert a US State in ISO-3166-2:US Format
def format_us_state(state):
    # open csv of ISO codes
    with open("iso_3166_2_us.csv") as f:
        file = csv.DictReader(f, delimiter=',')
        for line in file:
            if (line['Full State'] == state) or (line['Short State'] == state) or (line['ISO-3166-2'] == state):
                # return ISO code on match
                return line['ISO-3166-2']
    # do nothing for non-matches
    return state


# Get the weather for a location from the API endpoint
def get_current_weather(api_endpoint, location, api_key, lang=DEFAULT_API_LANG, units='standard'):
    # build API endpoint and query
    endpoint = f'http://{api_endpoint}/data/2.5/weather?q={location}&appid={api_key}&lang={lang}&units={units}'
    try:
        resp = requests.get(endpoint)
        return resp
    except:
        # TODO add error handling for 300s, 400s, 500s
        # TODO add retry policy
        print()


# Prepare the output
def format_weather_response(response, units):
    weather_json = response.json()
    pprint.pprint(weather_json)
    # get temperature from json object
    temp = round(weather_json['main']['feels_like'])
    # get correct degree suffix
    unit = get_degree_suffix(units)
    # TODO get name if it exists
    city = weather_json['name']
    print(f'It is currently {temp}{unit} in {city}.')
    return temp


# Convert unit selection to text
def get_degree_suffix(units):
    if units is 'standard':
        suffix = 'K'
    elif units is 'metric':
        suffix = '°C'
    else:
        suffix = '°F'
    return suffix


# Output the weather
def output_weather(output):
    print(output)


# Create a parser for commandline arguments
def get_parser(version):
    parser = argparse.ArgumentParser(
        description='Get the current weather from a specified location through the OpenWeather API.')
    parser.add_argument('--units', dest='units', default='imperial', choices=['imperial', 'metric', 'standard'])
    parser.add_argument('--version', action='version', version='%(prog)s v{}'.format(version))
    return parser


# Parse the arguments for the given parser
def parse_args(parser):
    return parser.parse_args()


def main():
    parser = get_parser(VER_NO)
    args = parse_args(parser)

    location = get_location_from_user()
    # response = get_current_weather(DEFAULT_API_ENDPOINT, location, DEFAULT_API_KEY, lang=DEFAULT_API_LANG, units=args.units)
    # weather_output = format_weather_response(response, args.units)
    # output_weather(weather_output)


if __name__ == '__main__':
    main()
