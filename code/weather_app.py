import os
import streamlit as st
import pandas as pd 
import numpy as np
from PIL import Image

# Custom imports 
from multipage import MultiPage
from pages import current_forecast_details, location_details, manage_locations, forecast_changes

app = MultiPage()

st.title("Backpacking Weather")

col1, col2 = st.columns(2)
app.add_page("Forecast Changes", forecast_changes.app)
app.add_page("Manage Locations", manage_locations.app)
app.add_page("Latest Forecast", current_forecast_details.app)
app.add_page("General", location_details.app)

app.run()

