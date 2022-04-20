import requests
import csv
from dagster import job, op, get_dagster_logger, ScheduleDefinition, DefaultScheduleStatus, schedule
import psycopg2
import requests
from weather.jobs.utils import insert_into, grab_columns_from_table, grab_query, clean_up




@op(config_schema={"host":str, "database":str, "user":str, "password":str, "tables":dict})
def set_up_tables(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    table_dict= context.op_config['tables']
    tables = table_dict.keys()

    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

    cur = conn.cursor()

    for table in tables:
        columns = ', '.join([ name+' '+typee for name, typee in table_dict[table].items()])
        commands = [f""" CREATE TABLE IF NOT EXISTS {table}({columns})""", f"""DROP TABLE {table}""", f"""CREATE TABLE IF NOT EXISTS {table}({columns})"""]
        for command in commands:
            cur.execute(command)


    commands = [f""" INSERT INTO LOCATIONS(_id, end_date, lat, lon, name, start_date, generated) 




    VALUES ('https://api.weather.gov/points/37.8651,-119.5383', '2022-04-15', 37.8651, -119.5383, 'Yosemite', '2022-04-10',FALSE ),
    ('https://api.weather.gov/points/37.7567,-119.5968', '2022-04-15', 37.7567, -119.5968, 'Yosemite Falls', '2022-04-10',FALSE )"""]
    for  i in commands:
        cur.execute(i)
    cur.close()
    conn.commit()
  
# def try_postgres():
#     conn = psycopg2.connect(
#     host="localhost",
#     database="TEST",
#     user="postgres",
#     password="")
#     return(conn)

# def create_table(conn):
#     command = """CREATE TABLE IF NOT EXISTS example(name VARCHAR(255) )"""
#     cur = conn.cursor()
#     cur.execute(command)
#     cur.close()
#     conn.commit()

# @op
# def insert_into_postgres():
#     conn = try_postgres()
#     create_table(conn)
#     command = """INSERT INTO example(name) VALUES ('maria');"""
#     cur = conn.cursor()
#     cur.execute(command)
#     cur.close()
#     conn.commit()
#     return 0
# @op
# def read_from_postgres(conn):
#     command = """SELECT * FROM example"""
#     cur = conn.cursor()
#     cur.execute(command)
#     records = cursor.fetchall()
#     for row in records:
#         print(row)
#     return 0


@op(config_schema={"host":str, "database":str, "user":str, "password":str, "locations_table":str, "requests_table":str, "forecasts_table":str})
def check_tables(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    locations_table= context.op_config['locations_table']
    requests_table= context.op_config['requests_table']
    forecasts_table= context.op_config['forecasts_table']

    query = f"""SELECT '{locations_table}', count(DISTINCT _id) FROM {locations_table}
    UNION ALL
    SELECT '{requests_table}', count(DISTINCT _id) FROM {requests_table}
    UNION ALL
    SELECT '{forecasts_table}', count(*) as raw FROM {forecasts_table}
    """

    base_stats = grab_query(host, database, user, password, query)
    print('\n'.join([str(i) for i in base_stats]))



    query =f"""
    with base as (
        SELECT _id as location_id,
        count(*) as num_forecasts
        FROM {forecasts_table} 
        group by 1
        ),

        base2 as (
        SELECT distinct _id, forecast FROM {requests_table}
        )
        SELECT locations._id, locations.generated, forecast, num_forecasts FROM {locations_table}
        left outer join base2 on locations._id = base2._id
        left outer join base 
        on locations._id = base.location_id
        


    """

    summary = grab_query(host, database, user, password, query)
    print('\n'.join([str(i) for i in summary]))

    print('=======================================')
    query = f"""SELECT * FROM {requests_table} 
        """

    requests_sample = grab_query(host, database, user, password, query)
    print('\n'.join([str(i) for i in requests_sample]))
    print('=======================================')


    query = f"""SELECT * FROM {forecasts_table} 
        """

    forecast_sample = grab_query(host, database, user, password, query)
    print('\n'.join([str(i) for i in forecast_sample]))


@op(config_schema={"host":str, "database":str, "user":str, "password":str, "locations_table":str, "requests_table":str, "forecasts_table":str})
def clean_up_locations(context):
    host= context.op_config['host']
    database= context.op_config['database']
    user= context.op_config['user']
    password= context.op_config['password']
    locations_table= context.op_config['locations_table']
    requests_table= context.op_config['requests_table']
    forecasts_table= context.op_config['forecasts_table']
    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

    cur = conn.cursor()
    

    filterr = f""" WHERE LAT > 71.3888 or LAT < 18.4655 or lon > -64.565 or lon < -179.148611
    """
    clean_up(host, database, user, password, locations_table, if_filter=filterr)







@job
def clean_up_locations_job():
    clean_up_locations()


@schedule(
   cron_schedule="15 * * * *",
   job=clean_up_locations_job,
   default_status=DefaultScheduleStatus.RUNNING
)
def clean_up_locations_schedule(context):
    with open(
        '/opt/code/config/clean_up_locations.yaml',
        "r",
    ) as fd:
         return yaml.safe_load(fd.read())




@job
def check_state():
    check_tables()

@job 
def prebuild_locations_job():
    set_up_tables()