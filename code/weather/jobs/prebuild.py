import requests
import csv
from dagster import job, op, get_dagster_logger
import psycopg2
import requests



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


    commands = [f""" INSERT INTO LOCATIONS(_id, end_date, lat, lon, name, start_date) 
    VALUES ('https://api.weather.gov/points/39.7456,-97.0892', '2022-04-15', 39.7456, -97.0892, 'Sample Location', '2022-04-10')"""]
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


@job 
def prebuild_locations_job():
    set_up_tables()