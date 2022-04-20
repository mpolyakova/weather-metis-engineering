from dagster import RunRequest, ScheduleDefinition, job, op, repository, sensor, DefaultScheduleStatus


from .jobs.prebuild import prebuild_locations_job, clean_up_locations_job, clean_up_locations_schedule
from .jobs.read_weather import  get_forecasts_job, get_location_details_job, forecast_schedule, get_new_location_details_job, new_location_details_schedule
from  .jobs.location import generate_loc, generate_locations_schedule
from .jobs.prebuild import check_state


@repository
def hello_world_repository():
    return [
    prebuild_locations_job, get_forecasts_job, get_location_details_job, generate_loc, check_state, forecast_schedule, get_new_location_details_job, generate_locations_schedule,new_location_details_schedule, clean_up_locations_job, clean_up_locations_schedule
    ]
