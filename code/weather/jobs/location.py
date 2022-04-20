import requests
import csv
from dagster import job, op, get_dagster_logger,ScheduleDefinition, DefaultScheduleStatus, schedule
import psycopg2
import requests


from weather.jobs.utils import insert_into, grab_columns_from_table, grab_query, clean_up

import numpy as np
from datetime import datetime
#Reference: https://stackoverflow.com/questions/69409596/how-can-i-create-grid-of-coordinates-from-a-center-point-in-python

def generate_grid(lat, lon, coors, dist):
    # lat, lon, coors, dist = (37.8651,-119.5383, 5, 2500)
    #Creating the offset grid
    mini, maxi = -dist*coors, dist*coors
    n_coord = coors*2+1
    axis = np.linspace(mini, maxi, n_coord)
    X, Y = np.meshgrid(axis, axis)


    #avation formulate for offsetting the latlong by offset matrices
    R = 6378137 #earth's radius
    dLat = X/R
    dLon = Y/(R*np.cos(np.pi*lat/180))
    latO = lat + dLat * 180/np.pi
    lonO = lon + dLon * 180/np.pi
    print("Starting point generation")

    #stack x and y latlongs and get (lat,long) format
    output = np.stack([latO, lonO]).transpose(1,2,0)
    output.shape
    print(output)
    return output


@op(config_schema={"host":str, "database":str, "user":str, "password":str,'locations_table':str, 'num_points':int, 'distance_in_m':int})
def generate_locations_around_original(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    locations_table= context.op_config['locations_table']
    num_points= context.op_config['num_points']
    distance_in_m= context.op_config['distance_in_m']
    query = f""" SELECT distinct * FROM {locations_table} where not generated """
    results = grab_query(host, database, user, password, query)
    print(results)
    new_locs = []
    for i in range(0,len(results)):
        row = results[i]
        grid_points = generate_grid(row[3], row[4], num_points, distance_in_m)
        end_date = datetime.now() if row[1] is None else row[1]
        start_date = datetime.now() if row[6] is None else row[6]
        counter = 0
        print(grid_points)
        for direction in grid_points:
            for j in direction:
                lat = format(round(j[0],4),'.4f')
                lon = format(round(j[1],4),'.4f')
                # (_id, end_date, lat, lon, name, start_date, generated) 
                holder = {}
                holder['_id']=f"""https://api.weather.gov/points/{lat},{lon}"""
                holder['end_date'] = end_date
                holder['lat'] = lat
                holder['lon'] = lon
                holder['name'] = row[5]+str(counter)
                holder['start_date']=start_date
                holder['generated']=True
                counter+=1
                new_locs.append(holder)
    clean_up(host, database, user, password, locations_table, "WHERE GENERATED")
    insert_into(host, database, user, password, locations_table, new_locs)







@job 
def generate_loc():
    generate_locations_around_original()



@schedule(
   cron_schedule="15 0 * * *",
   job=generate_loc,
   default_status=DefaultScheduleStatus.RUNNING
)
def generate_locations_schedule(context):
    with open(
        '/opt/code/config/generate_locs.yaml',
        "r",
    ) as fd:
         return yaml.safe_load(fd.read())

    