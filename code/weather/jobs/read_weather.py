import requests
import csv
from dagster import job, op, get_dagster_logger
import psycopg2
import requests


from weather.jobs.utils import insert_into, grab_columns_from_table


WEATHER_BASE = ["https://api.weather.gov/points/39.7456,-97.0892"]


@op
def get_links():
    return(WEATHER_BASE)

@op(config_schema={"host":str, "database":str, "user":str, "password":str, "request_table":str})
def get_point_details(context, links):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    request_table = context.op_config['request_table']

    for link in links:
        response_raw = requests.get(link)
        response = response_raw.json()
        simplified_response = {}
        simplified_response['_id'] = response['properties']['@id']
        simplified_response['forecast_office'] = response['properties']['gridId']
        simplified_response['gridx'] = response['properties']['gridX']
        simplified_response['gridy'] = response['properties']['gridY']
        simplified_response['forecast'] = response['properties']['forecast']
        simplified_response['forecast_hourly'] = response['properties']['forecastHourly']
        simplified_response['nearby_city'] = response['properties']['relativeLocation']['properties']['city']
        simplified_response['nearby_state'] = response['properties']['relativeLocation']['properties']['state']
        insert_into(host, database, user, password, request_table, simplified_response)
        print(simplified_response)
    return request_table



def grab_forecast_results(row, columns):
    link = row[1]
    response_raw = requests.get(link)
    response = response_raw.json()

    all_forecasts = []
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




@op(config_schema={"host":str, "database":str, "user":str, "password":str,'forecast_table':str})
def get_forecast(context, request_table):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    forecast_table = context.op_config['forecast_table']

    columns = ['_id', 'forecast']
    results = grab_columns_from_table(host, database, user, password, request_table, columns)
    for row in results:
        result = grab_forecast_results(row, columns)
        print(result)
        insert_into(host, database, user, password, forecast_table, result)

        



@job 
def handle_all_locations():
    get_forecast(get_point_details(get_links()))
    