import requests
import csv
from dagster import job, op, get_dagster_logger
import psycopg2
import requests

def try_postgres():
    conn = psycopg2.connect(
    host="localhost",
    database="TEST",
    user="postgres",
    password="")
    return(conn)

def create_table(conn):
    command = """CREATE TABLE IF NOT EXISTS example(name VARCHAR(255) )"""
    cur = conn.cursor()
    cur.execute(command)
    cur.close()
    conn.commit()

@op
def insert_into_postgres():
    conn = try_postgres()
    create_table(conn)
    command = """INSERT INTO example(name) VALUES ('maria');"""
    cur = conn.cursor()
    cur.execute(command)
    cur.close()
    conn.commit()
    return 0
@op
def read_from_postgres(conn):
    command = """SELECT * FROM example"""
    cur = conn.cursor()
    cur.execute(command)
    records = cursor.fetchall()
    for row in records:
        print(row)
    return 0


@job 
def hello_cereal_job():
    insert_into_postgres()