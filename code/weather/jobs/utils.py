import requests
import csv
from dagster import job, op, get_dagster_logger
import psycopg2
import requests
import datetime
import numpy as np


def convert_to_insert_strings(x):
    if isinstance(x, (datetime.datetime)):
        x = str(x.date())

    if x is None:
        x = ""

    if type(x) == type(1.0) or type(x) == type(1) or type(x) == type(True) or isinstance(x, (np.floating)):
        return str(x)
    else:
        return "'"+x+"'"

def insert_into(host, database, user,password, table, thing_to_insert):
    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

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

def grab_columns_from_table(host, database, user, password, table, columns):
    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

    cur = conn.cursor()

    command = f"""SELECT DISTINCT {','.join(columns)} FROM {table}"""
    cur.execute(command)
    records = cur.fetchall()
    return records



def clean_up(host, database, user, password, table, if_filter=None):
    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

    cur = conn.cursor()

    if if_filter is None:
        cur.execute(f'TRUNCATE TABLE {table}')
    else:
        cur.execute(f"""DELETE FROM {table} {if_filter}""")


def grab_query(host, database, user, password, query):
    conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password)

    cur = conn.cursor()

   
    cur.execute(query)
    records = cur.fetchall()
    return records

