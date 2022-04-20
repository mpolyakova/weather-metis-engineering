# Backpacking Weather

## Introduction
Backpacking planning is a lot of steps, from food to gear to location planning. In the Sierra Nevada, as well as many other areas, weather can differ significantly along a days route due to elevation changes. When planning a multiday trip, weather has to be considered, both for selecting the right gear, and not ending up in a dangerous situation, such as near summits during storms. 
Each backpacker attempts to resolve the problem in their own way, but currently, the common format is manually checking and rechecking weather along key points along the planned route - if multiple routes are considered, along each route. This is highly inefficient, and can lead to missed weather cues and potential mishaps. We propose an app which takes input locations and expands the monitored points in all directions, and then presents the latest forecast to the user. 

## Design 
The pipeline will have a preset location for Yosemite National Park, and take in additional user input. For each of the inputted locations, we will generate additional points around the location, and monitor forecasts at each of the locations on an ongoing basis in the following manner: 
### Weather.gov Api
The api is free to use for the public. Areas in the United States are divided into a 2.5km by 2.5km grid, with a separate forecast for each. In order to access the forecast, one must collect a forecast link for the location, and then query that forecast link. The links can change, but it is uncommon.  
The forecast link will be the same for each location within the same square.  
The API has "reasonable limits", and will occasionally fail requests. 
### Job overview  
#### User Input and Location Generation
We request a location name, and lat and lon coordinates, which we store in a postgres database table called locations. Additionally, we prebuild the database with 2 locations - Yosemite Falls and Yosemite Valley - my favorites. These can be removed from the app if desired.  
Each of the inputted locations is supplemented with generated locations around the area, in 2.5km increments in every direction (to match the grid). This is a separate job in Dagster, and runs both on a schedule(hourly), and is triggered when adding a new location in the application. 


#### Collection Location Details
This step collects locations details for each of the locations in the locations table. The primary detail collected in a forecast link described above. This job stores the link, as well as other metadata about the location in a location_requests table in the postgres database.  
The job comes in 2 flavors: full refresh, and new locations only. The full refresh will empty the table, and rescrape details for each location, good for setting up new locations, and restarting.  The new locations will query details for locations which don't already have details in the details table.  
The new locations job runs one an hour from dagster on a schedule. 

#### Forecasts 
Forecasts are collected using the forecast link in the details table, and stored in the forecasts table. We generate a separate row per location, update and day so we're able to query a specific forecast. 
This job runs hourly from dagster. 


### Pipeline Structure
The pipeline is containerized inside a Docker container, and run locally using port forwarding to display dagster and streamlit information.  
The pipeline contains 3 major pieces

#### Postgres database
The database is a local instance, and gets cleared every time docker is restarted. In V1 of this app, the db would be removed from the container and hosted in the cloud.  
It contains 3 tables - locations, location_requests and forecasts, corresponding to the three pieces described about.  It is created as part of the container entrypoint, and pre-populated using a one off Dagster job called prebuild. 

#### Dagster
Dagster manages the scheduled pieces of the pipeline - the forecast and details gathering, and location generation. We've created a weather python module containing the job code for these key pieces, under the same config. The forecasts, details collection and location generation are scheduled. 

#### Streamlit 
The Streamlit app contains three pages, selectable from a dropdown on the left hand side. 

##### Locations
The location details are in the background page, displaying location names and generated points in a map. 
![image](https://github.com/mpolyakova/weather-metis-engineering/blob/master/code/images/background-full-page.png)


##### Latest Forecast
This page displays the latest forecasts for points around a location. It defaults to the average of all user inputted locations, but a dropdown on the left side will focus and zoom on a specific location.  
The page contains two maps - one with the average temperatures forecasted for each location for the next ten days, and one allowing to select a specific day and look at the latest forecast using a slider.  


##### Location Management
This page allows the user to control locations for which we gather forecasts. The page allows users to add a location, using a name and latitude and longtitude. These are inserted into the locations, and trigger a one-off run of the location generation, and details gathering jobs.  
The page also allows users to remove locations using a dropdown. After confirming, the location is removed from the database, and the locations generate job is triggered to clear the previously generated location. 

## Tools 
Numpy and pandas for dataframe handling, and location generation
Yaml and pyaml for config handling
Dagster for job defintions and scheduling
Streamlit for app deployment. 
Postgres for data storage
Docker for containerizing 
Request for data scraping 










