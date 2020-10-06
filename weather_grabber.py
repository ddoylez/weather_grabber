import argparse
import csv
import pytest
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()
DEFAULT_API_KEY = os.getenv('API_APP_ID')
DEFAULT_API_ENDPOINT = os.getenv('API_ENDPOINT')
DEFAULT_API_LANG = os.getenv('API_LANG')
DEFAULT_LINE_LENGTH = os.getenv('LINE_LENGTH')
VER_NO = os.getenv('VERSION_NUMBER')


# Convert a US State to ISO-3166-2:US Format
def format_us_state(state):
    state_caps = state.upper()
    # open csv of ISO codes
    with open("iso_3166_2_us.csv") as f:
        file = csv.DictReader(f, delimiter=',')
        for line in file:
            if (line['Full State'].upper() == state_caps) or (line['Short State'].upper() == state_caps) or (
                    line['ISO-3166-2'].upper() == state_caps):
                # return ISO code on match
                return line['ISO-3166-2']
    # do nothing for non-matches
    return state


# Prepare the output
def format_weather_response(response, units):
    weather_json = response.json()
    # get temperature from json object
    temp = round(weather_json['main']['feels_like'])
    # get correct degree suffix
    unit = get_degree_suffix(units)
    str_out = f'It is currently {temp}{unit}'
    try:
        city = weather_json['name']
        str_out += f' in {city}'
    except KeyError:
        # ignore the name attribute if it is not found
        pass

    return str_out


# Get the weather for a location from the API endpoint
def get_current_weather(api_endpoint, location, api_key, lang=DEFAULT_API_LANG, units='imperial'):
    # build API endpoint and query
    endpoint = f'{api_endpoint}?q={location}&appid={api_key}&lang={lang}&units={units}'
    resp = requests.get(endpoint)
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    return resp


# Convert unit selection to text
def get_degree_suffix(units):
    if units == 'standard':
        suffix = 'K'
    elif units == 'metric':
        suffix = '°C'
    else:
        suffix = '°F'
    return suffix


# Get input from commandline args
def get_location_from_args(args):
    if args.state is None:
        location = f'{args.city}'
    else:
        state = format_us_state(args.state)
        location = f'{args.city},{state}'
    return location


# Get input from the user
def get_location_from_user():
    user_input = input('Where are you? (City, State)\n')
    matches = get_location_from_str(user_input)

    city_raw = None
    try:
        city_raw = matches.group(1).strip()
    except TypeError:
        print('Invalid location entered...\nPlease try somewhere else.')
        exit(1)

    state_raw = matches.group(3).strip()
    state = None
    if state_raw is not None:
        state = format_us_state(state_raw)

    if state is None:
        location = f'{city_raw}'
    else:
        location = f'{city_raw},{state}'
    return location


# Regex search a string for (City, State)
def get_location_from_str(str):
    matches = re.search('([A-Za-z ]+)(, ?([A-Za-z ]+)?)?', str)
    return matches


# Create a parser for commandline arguments
def get_parser(version):
    parser = argparse.ArgumentParser(
        description='Get the current weather from a specified location through the OpenWeatherMap API.')
    parser.add_argument('--city', dest='city', help='any city worldwide')
    parser.add_argument('--state', dest='state', help='US state of entered city')
    parser.add_argument('--lang', dest='lang', default=DEFAULT_API_LANG, help='abbreviated language code')
    parser.add_argument('--units', dest='units', default='imperial', choices=['imperial', 'metric', 'standard'],
                        help='choose between Fahrenheit, Celsius, or Kelvin units')
    parser.add_argument('--version', action='version', version='%(prog)s v{}'.format(version))
    return parser


# Output the weather
def output_weather(output):
    print(output)


# Parse the arguments for the given parser
def parse_args(parser):
    return parser.parse_args()


def main():
    parser = get_parser(VER_NO)
    args = parse_args(parser)

    if args.city is not None:
        location = get_location_from_args(args)
    else:
        location = get_location_from_user()
    try:
        response = get_current_weather(DEFAULT_API_ENDPOINT, location, DEFAULT_API_KEY, lang=args.lang,
                                       units=args.units)
        weather_output = format_weather_response(response, args.units)
        output_weather(weather_output)
    except requests.HTTPError as e:
        print(e)
        exit(1)
    except requests.ConnectionError as e:
        print(e)
        exit(1)

    exit(0)


# Test cases for pytest to run
class TestWeather:
    # Test "conversion" of an ISO code
    def test_state_iso(self):
        assert format_us_state('US-IL') == 'US-IL'

    # Test conversion of a full state name
    def test_state_long(self):
        assert format_us_state('wisconsin') == 'US-WI'

    # Test conversion of a short state name
    def test_state_short(self):
        assert format_us_state('iA') == 'US-IA'

    # Confirm that the API is responding with results
    def test_api_call(self):
        assert get_current_weather(DEFAULT_API_ENDPOINT, 'Chicago,US-IL', DEFAULT_API_KEY).status_code == requests.codes.ok

    # Confirm kelvin units are returned
    def test_unit_kelvin(self):
        assert get_degree_suffix('standard') == 'K'

    # Confirm celsius units are returned
    def test_unit_celsius(self):
        assert get_degree_suffix('metric') == '°C'

    # Confirm fahrenheit units are returned
    def test_unit_fahrenheit(self):
        assert get_degree_suffix('imperial') == '°F'

    # Test that cities are the default detection
    def test_regex_single_city(self):
        assert get_location_from_str('Chicago').group(1) == 'Chicago'

    # Test that spaces are included in city detection
    def test_regex_triple_cty(self):
        assert get_location_from_str('Salt Lake City').group(1) == 'Salt Lake City'

    # Test that spaces are included in state detection
    def test_regex_double_state(self):
        assert get_location_from_str('New York, New York').group(3) == 'New York'

    # Test that a blank entry breaks the regex
    def test_regex_blank(self):
        matches = get_location_from_str('')
        assert matches is None

    # Test that numbers are not picked up as a city
    def test_regex_numeric_city(self):
        matches = get_location_from_str('123, Iowa')
        assert (matches.group(1) == ' Iowa') and (matches.group(3) != 'Iowa')

    # Test that numbers are not picked up as a state
    def test_regex_numeric_state(self):
        matches = get_location_from_str('Des Moines, 456')
        assert (matches.group(1) == 'Des Moines') and (matches.group(3) != '456')

    # Test that missing commas will affect state detection
    def test_regex_city_state(self):
        matches = get_location_from_str('Chicago IL')
        assert (matches.group(1) == 'Chicago IL') and (matches.group(3) is None)

    # Test that commas correctly detect states
    def test_regex_city_comma_state(self):
        matches = get_location_from_str('Chicago, IL')
        assert (matches.group(1) == 'Chicago') and (matches.group(3) == 'IL')


if __name__ == '__main__':
    main()
