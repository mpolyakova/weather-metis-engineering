import requests
import csv
from dagster import job, op, get_dagster_logger, ScheduleDefinition, DefaultScheduleStatus, schedule
import psycopg2
import requests
import time
import yaml
import os

from weather.jobs.utils import insert_into, grab_columns_from_table, clean_up, grab_query


headers = requests.utils.default_headers()

# Update the headers with your custom ones
# You don't have to worry about case-sensitivity with
# the dictionary keys, because default_headers uses a custom
# CaseInsensitiveDict implementation within requests' source code.
headers.update(
    {
        'User-Agent': 'Maria Polyakova Data Gathering for Student Project',
    }
)



@op(config_schema={"host":str, "database":str, "user":str, "password":str, "locations_table":str})
def get_links(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    locations_table = context.op_config['locations_table']
    columns = ['_id']
    results = grab_columns_from_table(host, database, user, password, locations_table, columns)
    return([i[0] for i in results ])



@op(config_schema={"host":str, "database":str, "user":str, "password":str, "locations_table":str, "location_responses_table":str})
def get_not_matched_links(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    locations_table = context.op_config['locations_table']
    location_responses_table = context.op_config['location_responses_table']
    query = f"""
    SELECT DISTINCT _ID FROM 
    (
    SELECT l._ID, r._id as request_loc 
    FROM {locations_table} l LEFT OUTER JOIN {location_responses_table} r ON  l._id = r._id 
    
    ) f
    WHERE request_loc is null
    """
    results = grab_query(host, database, user, password,query)
    if len(results) > 0:
        return([i[0] for i in results ])

    else:
        return([])




@op(config_schema={"host":str, "database":str, "user":str, "password":str, "request_table":str, "wait_time":int, "full_refresh":bool})
def get_location_details(context, links):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    request_table = context.op_config['request_table']
    wait_time = context.op_config['wait_time']
    full_refresh = context.op_config['full_refresh']
    if(full_refresh):
        clean_up(host, database, user, password, request_table)
    simplified_responses = []
    for link in links:
        print(link)
        try:
            response_raw = requests.get(link, headers=headers)
            response = response_raw.json()
            simplified_response = {}
            simplified_response['_id'] = link
            simplified_response['forecast_office'] = response['properties']['gridId']
            simplified_response['gridx'] = response['properties']['gridX']
            simplified_response['gridy'] = response['properties']['gridY']
            simplified_response['forecast'] = response['properties']['forecast']
            simplified_response['forecast_hourly'] = response['properties']['forecastHourly']
            simplified_response['nearby_city'] = response['properties']['relativeLocation']['properties']['city']
            simplified_response['nearby_state'] = response['properties']['relativeLocation']['properties']['state']
            simplified_responses.append(simplified_response)
            time.sleep(wait_time)
        except:
            continue
    if len(simplified_responses) > 0:
        insert_into(host, database, user, password, request_table, simplified_responses)



def grab_forecast_results(row, columns):
    # print('+++++++++++++++++++++++++++++++++++++++++')
    link = row[1]
    # print("Id: "+row[0])
    # print(link)
    try:
        response_raw = requests.get(link, headers=headers)
        response = response_raw.json()
    except:
        os.sleep(5)
        response_raw = requests.get(link, headers=headers)
        response = response_raw.json()

    all_forecasts = []
    # xprint(response)
    try:
        for forecast in response['properties']['periods']:
            simplified_response = {}
            for i in range(0, len(row)):
                simplified_response[columns[i]] = row[i]
            simplified_response['updated'] = response['properties']['updated']
            simplified_response['elevation'] = response['properties']['elevation']['value']
            simplified_response['forecast_type'] = response['properties']['forecastGenerator']
            simplified_response['start_time'] = forecast['startTime']
            simplified_response['end_time'] = forecast['endTime']
            simplified_response['is_daytime'] = forecast['isDaytime']
            simplified_response['temp'] = forecast['temperature']
            simplified_response['wind_speed'] = forecast['windSpeed']
            simplified_response['wind_dir'] = forecast['windDirection']
            simplified_response['short'] = forecast['shortForecast']
            all_forecasts.append(simplified_response)
        return all_forecasts
    except:
        try:
            return(grab_forecast_results(row, columns))

        except:
            return None




@op(config_schema={"host":str, "database":str, "user":str, "password":str,'request_table':str,'forecast_table':str, 'wait_time':int})
def get_forecast(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    request_table= context.op_config['request_table']
    forecast_table = context.op_config['forecast_table']
    wait_time = context.op_config['wait_time']

    columns = ['_id', 'forecast']
    results = grab_columns_from_table(host, database, user, password, request_table, columns)
    print(len(results))
    print(results)
    for row in results:
        result = grab_forecast_results(row, columns)
        if result is not None:
            insert_into(host, database, user, password, forecast_table, result)
        time.sleep(wait_time)



@job 
def get_location_details_job():
    get_location_details(get_links())


@job
def get_new_location_details_job():
    get_location_details(get_not_matched_links())


@schedule(
   cron_schedule="15 * * * *",
   job=get_new_location_details_job,
   default_status=DefaultScheduleStatus.RUNNING
)
def new_location_details_schedule(context):
    with open(
        '/opt/code/config/get_new_locations.yaml',
        "r",
    ) as fd:
         return yaml.safe_load(fd.read())






@job 
def get_forecasts_job():
    get_forecast()





@schedule(
   cron_schedule="0,30 * * * *",
   job=get_forecasts_job,
   default_status=DefaultScheduleStatus.RUNNING
)
def forecast_schedule(context):
    with open(
        '/opt/code/config/forecast.yaml',
        "r",
    ) as fd:
         return yaml.safe_load(fd.read())
