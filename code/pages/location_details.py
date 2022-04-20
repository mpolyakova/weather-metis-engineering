
import matplotlib.pyplot as plt
import pandas as pd

from dotenv import load_dotenv
import pandas as pd 
import psycopg2
import os
from  datetime import date
import pydeck as pdk
from PIL import Image
import numpy as np


# import folium # map rendering library
import streamlit as st #creating an app
# from streamlit_folium import folium_static 
#using folium on streamlit
# from multipage import MultiPage
# from pages import data_upload, machine_learning, metadata, data_visualize, redundant, inference # import your pages here

#referenc: https://naysan.ca/2020/05/31/postgresql-to-pandas/
# https://github.com/prakharrathi25/data-storyteller

from pages.utils import postgresql_to_dataframe, base_query, get_postgres, insert_into


def app():
    display = Image.open('images/Yosemite-beautiful-sun.jpg')
    display = np.array(display)
    st.image(display)

    load_dotenv()

    column_names = ['name','lat','lon']

    query = f"""
    SELECT DISTINCT {','.join(column_names)} FROM LOCATIONS WHERE NOT GENERATED
    """
    df = postgresql_to_dataframe(get_postgres(), query)

    st.write(
    ## Locations Monitored

    )

    st.dataframe(df)

    query = f"""
    {base_query}

    SELECT  DISTINCT LAT, LON FROM BASE

    """
    df2 = postgresql_to_dataframe(get_postgres(), query)

    # min_date = df2[''].min().date()
    # max_date = df2['forecast_end'].max().date()
    # price_input = st.slider(' Earliest Forecast Date', min_value=min_date, value=min_date, max_value=max_date)

    # # price_filter = df2['forecast_end'].dt.date> price_input
    st.map(df2[['lat', 'lon']])



 #    st.write(
 #    '''
 #    ## Elevations
 #       ''' )


 #    add_select = st.sidebar.selectbox("What data do you want to see?",("Elevation", "Latest Forecast"))
 #    folium.Map(tiles=add_select, )












 #    query = f"""
 #     with base as (SELECT DISTINCT _id, lat, lon, generated FROM locations ) ,
 #     elev as (SELECT _id, avg(elevation) as elevation FROM forecasts group by 1)
 #        SELECT base.*, elev.elevation from BASE JOIN ELEV ON BASE._ID = ELEV._ID

 #        """
 #    df2 = postgresql_to_dataframe(get_postgres(), query)
 #    st.dataframe(df2)

 #    st.pydeck_chart(pdk.Deck(
 #     map_style='mapbox://styles/mapbox/light-v9',
 #     initial_view_state=pdk.ViewState(
 #         latitude= df2['lat'].mean(),
 #         longitude=df2['lon'].mean(),
 #         zoom=11,
 #         pitch=50,
 #     ),
 #     layers=[
 #         pdk.Layer(
 #            'HexagonLayer',
 #            data=df2[['lat','lon','elevation']],
 #            get_position='[lon, lat]',
 #            radius=200,
 #            elevation_scale=4,
 #            elevation_range=[0, 1000],
 #            pickable=True,
 #            extruded=True,
 #         )
 #     ],
 # ))








