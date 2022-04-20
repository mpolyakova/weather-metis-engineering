
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
import pandas as pd 
import psycopg2
import os
import pydeck as pdk
import math
from pydeck.types import String

from datetime import datetime
import numpy as np

# from multipage import MultiPage
# from pages import data_upload, machine_learning, metadata, data_visualize, redundant, inference # import your pages here

#referenc: https://naysan.ca/2020/05/31/postgresql-to-pandas/
# https://github.com/prakharrathi25/data-storyteller


def get_postgres():
    conn = psycopg2.connect(
    host=os.getenv('DAGSTER_POSTGRES_HOST'),
    database=os.getenv('DAGSTER_POSTGRES_DB'),
    user=os.getenv('DAGSTER_POSTGRES_USERNAME'),
    password=os.getenv('DAGSTER_POSTGRES_PASSWORD'))
    return(conn)


def convert_to_insert_strings(x):
    if isinstance(x, (datetime)):
        x = str(x.date())

    if type(x) == type(1.0) or type(x) == type(1) or type(x) == type(True) or isinstance(x, (np.floating)):
        return str(x)
    else:
        return "'"+x+"'"

def insert_into(conn, table, thing_to_insert):
    cur = conn.cursor()
    print(thing_to_insert)
    if type(thing_to_insert) == type({}):

        columns = ', '.join(thing_to_insert.keys())
        values = ','.join([ convert_to_insert_strings(i) for i in thing_to_insert.values()])
        command = f""" 
            INSERT INTO {table}({columns}) VALUES ({values})
            """
    else:
        columns = ', '.join(thing_to_insert[0].keys())
        all_values = []
        for thing in thing_to_insert:
            x = ','.join([ convert_to_insert_strings(i) for i in thing.values()])
            all_values.append('('+x+')')
        values = ', \n'.join(all_values)

        command = f""" 
            INSERT INTO {table}({columns}) VALUES {values}
            """
    print(command)
    cur.execute(command)
    cur.close()
    conn.commit()


def delete_from(conn, table,filterr=None):
    if filterr is None:
        return
    else:
        cur = conn.cursor()
        command = f""" 
               DELETE FROM {table} {filterr}
                """
        
        print(command)
        cur.execute(command)
        cur.close()
        conn.commit()


def postgresql_to_dataframe(conn, select_query):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
        colnames = [desc[0] for desc in cursor.description ] #https://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()
    
    # We just need to turn it into a pandas dataframe

    df = pd.DataFrame(tupples,columns=colnames)
    return df


locations= 'locations'
forecasts= 'forecasts'
location_responses = 'location_responses'


base_query = f"""
        with forecastss as (
            SELECT distinct forecast, updated, elevation, start_time, end_time, is_daytime, temp, wind_speed, wind_dir, short FROM {forecasts} 
        ),

        non_gen as (
            SELECT DISTINCT FORECAST, I._ID  as _ID, lat, lon FROM {location_responses} r join (SELECT * FROM {locations} WHERE NOT GENERATED) I on r._id = i._id
        ),

        gen as (
           SELECT FORECAST, (ARRAY_AGG(I._ID))[1] as _ID, avg(lat) as lat, avg(lon) as lon FROM (select distinct forecast, _id FROM {location_responses} WHERE FORECAST NOT IN (SELECT DISTINCT FORECAST FROM NON_GEN) ) r
            join {locations} i
            ON r._ID = i._id
            GROUP BY 1

        ),

        responses as (
           SELECT * FROM NON_GEN 
           UNION 
           SELECT * FROM GEN
        ),


        base as (
            SELECT forecastss.*, responses._id, name, generated, responses.lat, responses.lon FROM FORECASTSS JOIN RESPONSES USING(FORECAST) JOIN {locations} ON LOCATIONS._ID = RESPONSES._ID
        )

"""