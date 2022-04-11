from dagster import RunRequest, ScheduleDefinition, job, op, repository, sensor


from .jobs.try_postgres import hello_cereal_job
from .jobs.prebuild import prebuild_locations_job
from .jobs.read_weather import handle_all_locations

@repository
def hello_world_repository():
    return [
    hello_cereal_job, prebuild_locations_job, handle_all_locations
    ]
