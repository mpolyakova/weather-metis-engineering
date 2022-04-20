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

from pages.utils import postgresql_to_dataframe, base_query, get_postgres
from PIL import Image
import numpy as np


def app():
    display = Image.open('images/yosemite-valley-snow.webp')
    display = np.array(display)
    st.image(display)

    load_dotenv()
    st.write( '''
    ## Latest Average Predicted Temp next 10 Days
    '''
    )


    query = f"""
        {base_query},

    base2 as ( SELECT _ID, MAX(updated) as latest_updated, COUNT(*) AS NUM_OBSERVATIONS FROM base GROUP BY 1

    ),

    base3 as (
    SELECT distinct base.*, base2.num_observations FROM BASE JOIN BASE2 ON BASE.UPDATED = BASE2.LATEST_UPDATED AND BASE._ID = BASE2._ID
    )

    SELECT distinct _ID, NAME, GENERATED, LAT, LON, avg(temp) as avg_predicted_temp FROM base3 group by 1,2,3,4,5
    """

    df2 = postgresql_to_dataframe(get_postgres(), query)
    # st.dataframe(df2)
    # print(df2)

    # forecast = pdk.Layer(
    # "HeatmapLayer",
    # data=df2,
    # get_position=['lon','lat'],
    # # color_range=COLOR_BREWER_BLUE_SCALE,
    # get_weight="avg_predicted_temp",
    # pickable=True
    # )
    df2['red_temp_holder']= (df2['avg_predicted_temp']-70)*17
    df2['green_temp_holder']= 255-abs(df2['avg_predicted_temp']-70)*8.5
    df2['blue_temp_holder']=255-abs(df2['avg_predicted_temp']-30)*6.375
    # df2['opacity']= 255 - max(df2['red_temp_holder'], df2['green_temp_holder'], df2['blue_temp_holder'])%255
    df2['opacity']=100
    df2['temp']=df2['avg_predicted_temp'].astype('int').astype('str')
    df2['degrees']='     F'



    only_names =['all']+ df2[~df2['generated']]['name'].unique().tolist()

    option = st.sidebar.selectbox(
     '(Optional) Select Location to Center On', only_names
     )

    if(option=='all'):
        middle_lat = df2['lat'].mean()
        middle_lon = df2['lon'].mean()
        zoom = 9
    else:
        middle_lat = df2[df2['name']==option]['lat'].mean()
        middle_lon = df2[df2['name']==option]['lon'].mean()
        zoom = 11

    layer = pdk.Layer(
    'ScatterplotLayer',
    data=df2,
    get_position=['lon', 'lat'],
    get_radius=500,  
    pickable=True,
    filled=True,
    get_fill_color='[red_temp_holder, green_temp_holder, blue_temp_holder, opacity]'
    )

    descriptions_temps = pdk.Layer(
    "TextLayer",
    df2,
    pickable=True,
    get_position=['lon', 'lat'],
    get_text='temp',
    get_size=16,
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
    # get_color=[255,255,255]
    get_color='[red_temp_holder, green_temp_holder, blue_temp_holder]'
    )
    descriptions_f = pdk.Layer(
    "TextLayer",
    df2,
    pickable=True,
    get_position=['lon', 'lat'],
    get_text='degrees',
    get_size=10,
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
    # get_color=[255,255,255]
    get_color='[red_temp_holder, green_temp_holder, blue_temp_holder]'
    )



    st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude= middle_lat,
         longitude=middle_lon,
         zoom=zoom
     ),
    layers=[
        descriptions_temps, descriptions_f, layer
    ]
    ))


   # st.dataframe(df2)


    st.write(
        '''
        ## Latest Prediction for Day

        '''

        )


    query = f"""
    {base_query},

    base2 as ( SELECT _ID, start_time, MAX(updated) as latest_updated, COUNT(*) AS NUM_OBSERVATIONS FROM base GROUP BY 1,2

    ),

    base3 as (
    SELECT distinct base.*, base2.num_observations FROM BASE JOIN BASE2 ON BASE.UPDATED = BASE2.LATEST_UPDATED AND BASE._ID = BASE2._ID AND BASE.START_TIME = BASE2.START_TIME
    )

    SELECT distinct _ID, NAME, GENERATED,LAT, LON, START_TIME::date AS day_predicted, avg(temp) as last_predicted_temp FROM base3 group by 1,2,3,4,5,6
    """
    df2 = postgresql_to_dataframe(get_postgres(), query)



    df2['day_predicted'] = df2['day_predicted']
    df2['avg_predicted_temp'] = df2['last_predicted_temp'].copy()


    min_day = df2['day_predicted'].min()
    max_day = df2['day_predicted'].max()
    start_time = st.slider(
     "When do you start?",
     min_value=min_day,
     max_value=max_day,
     value=max_day,
     format="MM/DD/YY")
    st.write("Predicted Day:", start_time)


    df2 = df2[df2['day_predicted']==start_time].copy()
    df2 = df2.drop(['day_predicted','last_predicted_temp'], axis=1)


    df2['red_temp_holder']= ((df2['avg_predicted_temp']-70)*17).astype('int')
    df2['green_temp_holder']= (255-abs(df2['avg_predicted_temp']-70)*8.5).astype('int')
    df2['blue_temp_holder']=(255-abs(df2['avg_predicted_temp']-30)*6.375).astype('int')
    df2['opacity']=100
    df2['temp']=df2['avg_predicted_temp'].astype('int').astype('str')
    # df2['degrees']=df2['name'].astype('str')+
    df2['degrees']='      F'

    layer = pdk.Layer(
    'ScatterplotLayer',
    data=df2,
    get_position=['lon', 'lat'],
    get_radius=500,  
    pickable=True,
    filled=True,
    get_fill_color='[red_temp_holder, green_temp_holder, blue_temp_holder, opacity]'
    )

    descriptions_temps = pdk.Layer(
    "TextLayer",
    df2,
    pickable=True,
    get_position=['lon', 'lat'],
    get_text="temp",
    get_size=16,
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
    # get_color=[255,255,255]
    get_color='[red_temp_holder, green_temp_holder, blue_temp_holder]'
    )


    descriptions_f = pdk.Layer(
    "TextLayer",
    df2,
    pickable=True,
    get_position=['lon', 'lat'],
    get_text='degrees',
    get_size=10,
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
    # get_color=[255,255,255]
    get_color='[red_temp_holder, green_temp_holder, blue_temp_holder]'
    )



    st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude= middle_lat,
         longitude=middle_lon,
         zoom=zoom
     ),
    layers=[layer,
        descriptions_temps, descriptions_f
    ]
    ))

