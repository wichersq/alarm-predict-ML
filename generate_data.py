import googlemaps
import pprint
import pandas as pd
from datetime import datetime, timedelta
import random
from googleplaces import GooglePlaces

"""Uses the google maps API and pandas to get the other features and saves the data to RESULT_FILE_NAME."""

def Get_Start_Location(address_str):
    """Specific city to start depends on arrival address"""
    START_ADDRESS = {'PA': 'Harrisburg, PA', 'MD': 'Cherry Hill, Baltimore, MD',
                     'DC': 'Washington, District of Columbia', 'NY': 'Queens, NY',
                     'NC': 'Fayetteville, NC', 'CT': 'Hartford, CT',
                     'VA': 'Charlottesville, VA', 'NJ': 'Vineland, NJ',
                     'SC': 'Swansea, South Carolina', 'MA': 'Worcester, MA'}

    lst_address = address_str.split(' ')
    state = lst_address[-2]
    return START_ADDRESS[state]


def Get_Place_ID(business_name, address):
    """Returns place_address with name and address of the business and also place_ID."""
    place_address = business_name + ', ' + address
    result = gmaps_get_place_ID.find_place(
        input=place_address, input_type='textquery')
    place_ID = result['candidates'][0]['place_id']
    return place_address, place_ID


def Get_Departure_Time():
    """Returns a random future time for travel"""
    now = datetime.now()
    rand_hour = random.randint(0, 23)
    rand_min = random.randint(0, 59)
    rand_sec = random.randint(0, 59)
    rand_microsec = random.randint(0, 999999)
    time = now.replace(hour=rand_hour, minute=rand_min,
                       second=rand_sec, microsecond=rand_microsec)
    time += timedelta(days=random.randint(1, 3))
    day_in_week = time.isoweekday()

    return time, day_in_week


def safe_index(dic, index):
    if index in dic:
        return dic[index]
    return "NA"


def Get_Store_Detail(place_ID):
    place = google_places.get_place(place_ID)
    place.get_details()
    detail = place.details

    if 'opening_hours' in detail and 'periods' in detail['opening_hours']:
        hours = detail['opening_hours']['periods']
    else:
        hours = 'NA'

    price_level = safe_index(detail, 'price_level')

    rating = safe_index(detail, 'rating')

    type_store = safe_index(detail, 'types')

    return hours, price_level, rating, type_store


def Convert_Hour_Period(period):
    lst_hr = ['NA'] * 14

    if period == 'NA':
        return lst_hr

    if len(period) == 1 and period[0]['open']['day'] == 0:
        lst_hr = [period[0]['open']['time']] * len(lst_hr)
    else:
        for n in range(len(period)):
            for status in period[n]:
                day = period[n][status]['day']
                pos = (day * 2)
                if status == 'open':
                    pos = pos + 1
                lst_hr[pos] = period[n][status]['time']
    return (lst_hr)


def convert_store_type(lst_type):
    """Convert the type of store from a list to a string for csv file."""
    string = ''
    for n in lst_type:
        string = string + n + ' '
    return string


api_key_file = open("API_KEY.txt", 'r')
API_KEY = api_key_file.readline().rstrip()

pp = pprint.PrettyPrinter(indent=2)

gmaps = googlemaps.Client(key=API_KEY, queries_per_second=50, retry_over_query_limit=False)
gmaps_get_place_ID = googlemaps.Client(key=API_KEY, queries_per_second=50, retry_over_query_limit=False)
google_places = GooglePlaces(API_KEY)

bussiness_address_df = pd.read_csv('Data/Places_info.csv')

Result_df = pd.DataFrame(columns=['Business Name', 'Destination Address',
                                  'Place ID', 'Type of Store', 'Rating',
                                  'Reviews', 'Price Level',
                                  'Day0_Close', 'Day0_Open',
                                  'Day1_Close', 'Day1_Open',
                                  'Day2_Close', 'Day2_Open',
                                  'Day3_Close', 'Day3_Open',
                                  'Day4_Close', 'Day4_Open',
                                  'Day5_Close', 'Day5_Open',
                                  'Day6_Close', 'Day6_Open',
                                  'Departure Time', 'Day of the Week',
                                  'Driving_Distance', 'Driving_Duration',
                                  'Walking_Distance', 'Walking_Duration',
                                  'Bicycling_Distance', 'Bicycling_Duration',
                                  'Transit_Distance', 'Transit_Duration'])

TRAVEL_BY = ["driving", "walking", "bicycling", "transit"]

RESULT_FILE_NAME = "Data/raw_data2.csv"

for n in range(len(bussiness_address_df)):
    info_lst = []

    business_name = bussiness_address_df['Business Name'][n]
    business_adr = bussiness_address_df['Address'][n]
    review = bussiness_address_df['Review'][n]

    try:
        end_loc, place_ID = Get_Place_ID(business_name, business_adr)  #
    except GooglePlaces.GooglePlacesError as err:
        continue

    start_loc = Get_Start_Location(business_adr)

    rand_time, day_of_week = Get_Departure_Time()

    open_hours, price_level, rating, type_store = Get_Store_Detail(place_ID)

    type_store_str = convert_store_type(type_store)

    info_lst = [business_name, business_adr, place_ID,  # a row of result file
                type_store_str, rating, review,
                price_level]
    # convert the open/close period (a dictionary) obtained from google place and put in a csv file
    lst_open_period = Convert_Hour_Period(open_hours)
    for m in lst_open_period:
        info_lst.append(m)
    # have different format for datetime to put in a csv file
    time_str = rand_time.isoformat(sep=' ')
    info_lst.append(time_str)
    info_lst.append(day_of_week)

    for transit in TRAVEL_BY:
        try:
            directions_result = gmaps.directions(start_loc, end_loc,
                                                 mode=transit, departure_time=rand_time)
            leg = directions_result[0]['legs'][0]
            distance = leg['distance']['value']
            duration = leg['duration']['value']
        except (IndexError or googlemaps.exceptions.ApiError) as err:
            distance = 'NA'
            duration = 'NA'

        info_lst.append(distance)
        info_lst.append(duration)

    Result_df.loc[n] = info_lst
    if n % 100 == 0:
        Result_df.to_csv(RESULT_FILE_NAME, index=False)

Result_df.to_csv(RESULT_FILE_NAME, index=False)
