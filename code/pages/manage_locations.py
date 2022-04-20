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

from pages.utils import postgresql_to_dataframe, base_query, get_postgres, insert_into, delete_from
import os
from dagster_graphql import DagsterGraphQLClient
from dagster_graphql import DagsterGraphQLClientError
import yaml
from PIL import Image
import numpy as np



client = DagsterGraphQLClient("localhost", port_number=3000)



def app():
    display = Image.open('images/firefall.jpg')
    display = np.array(display)
    st.image(display)

    load_dotenv()
    st.write( '''
    ## Current Locations
    '''
    )
    column_names = ['_id', 'name', 'lat','lon']

    query = f"""
    SELECT DISTINCT {','.join(column_names)} FROM LOCATIONS WHERE NOT GENERATED
    """
    df = postgresql_to_dataframe(get_postgres(), query)

    st.dataframe(df)



    st.write(
    '''
    # Add New Location

    '''
    )

    input_location = {}

    input_location['name'] = st.text_input('Enter Location Name')
    input_location['lat'] = st.text_input('Lat (4 decimal points)')
    input_location['lon'] = st.text_input('Lon (4 decimal points)')
    input_location['generated'] = False
    input_location['end_date'] = datetime.now()
    input_location['start_date']=datetime.now()


    if st.button('Insert into Database', key='blahblah'):
        with st.spinner("Training ongoing"):

            input_location['lat'] = float(input_location['lat'])
            input_location['lon'] =  float(input_location['lon'])
            if input_location['lat']>= 71.3888 or input_location['lat']<= 18.465556 or input_location['lon']>= -64.565 or input_location['lon']<=-179.148611 :
               st.write('Unsupported Location, sorry!')
               return
            else:
                input_location['lat'] = format(float(input_location['lat']),'.4f')
                input_location['lon'] = format(float(input_location['lon']),'.4f')
                input_location['_id'] = 'https://api.weather.gov/points/'+str(input_location['lat'])+','+str(input_location['lon'])

                insert_into(get_postgres(), 'LOCATIONS', input_location)
                st.write('Completed Insert')

                
                column_names = ['_id', 'name', 'lat','lon']

                query = f"""
                SELECT DISTINCT {','.join(column_names)} FROM LOCATIONS WHERE NOT GENERATED
                """
                df = postgresql_to_dataframe(get_postgres(), query)

                st.dataframe(df)

                try:
                    with open("/opt/code/config/generate_locs.yaml", 'r') as stream:
                        parsed_yaml=yaml.safe_load(stream)
                    new_run_id: str = client.submit_job_execution(
                        'generate_loc',
                        run_config=parsed_yaml,
                    )
                    st.write('Successfully generated locations around inserted point')
                except:
                    st.write('Unable to  start locations generator Job')
                    return

                try:
                    with open("/opt/code/config/get_new_locations.yaml", 'r') as stream:
                        parsed_yaml=yaml.safe_load(stream)
                    new_run_id: str = client.submit_job_execution(
                        'get_new_location_details_job',
                        run_config=parsed_yaml,
                    )
                    st.write('Location details successfully found. Now part of forecasts')
                except:
                    st.write('Unable to get details for location')
                    return

    st.write('''

        # Delete Locations
        ''')

    delete_the_following = st.multiselect(
     'Please Add Any Locations you would like to remove',
     df['name'].tolist(),
     [])

    st.write('You selected:', delete_the_following)
    if st.button('Confirm Delete'):
        if len(delete_the_following ) > 0:
            FILTERR = f""" 
                WHERE NAME in ({', '.join(["'"+i+"'" for i in delete_the_following ])})
            """
            delete_from(get_postgres(), 'LOCATIONS', FILTERR)

            column_names = ['_id', 'name', 'lat','lon']

            query = f"""
            SELECT DISTINCT {','.join(column_names)} FROM LOCATIONS WHERE NOT GENERATED
            """
            df = postgresql_to_dataframe(get_postgres(), query)

            st.dataframe(df)
            try:
                with open("/opt/code/config/generate_locs.yaml", 'r') as stream:
                    parsed_yaml=yaml.safe_load(stream)
                new_run_id: str = client.submit_job_execution(
                    'generate_loc',
                    run_config=parsed_yaml,
                )
                st.write('Generate Locations Cleaned Up')
            except:
                st.write('Unable to  start locations generator Job')
                return

        else:
            st.write('Nothing to delete')




