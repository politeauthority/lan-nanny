"""
Database handler.

Handles the raw database connections, and database initialization of tables and required values.q

"""
import os
import sqlite3
from sqlite3 import Error

from flask import g
import mysql.connector
from mysql.connector import Error

from .models.option import Option
from .models.alert import Alert
from .models.device import Device
from .models.device_port import DevicePort
from .models.device_witness import DeviceWitness
from .models.scan_port import ScanPort
from .models.scan_host import ScanHost
from .models.port import Port
from .models.entity_meta import EntityMeta
from .models.database_growth import DatabaseGrowth
from .models.sys_info import SysInfo
from .collections.options import Options

DATABASE_NAME = 'lan_nanny'

def connect_mysql(server: dict=None):
    """Connect to MySql database and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['host'],
            user=server['user'],
            password=server['pass'],
            database=server['name'])
        if connection.is_connected():
            db_Info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
    except Error as e:
        print("Error while connecting to MySQL", e)
    return connection, cursor


def connect_mysql_no_db(server):
    """Connect to MySql database and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['host'],
            user=server['user'],
            password=server['pass'])
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
    except Error as e:
        print("Error while connecting to MySQL", e)
    return connection, cursor


def create_mysql_database(conn, cursor):
    sql = """CREATE DATABASE IF NOT EXISTS %s""" % DATABASE_NAME
    cursor.execute(sql)
    print('Created database: %s' % DATABASE_NAME)


def create_connection(database_file: str):
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(database_file)
    except Error as e:
        print(e)
        exit(1)
    cursor = conn.cursor()
    return conn, cursor


def get_db_flask(database_file: str):
    """Create a database connection to a SQLite database for the flask web environment."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_file)
    return db, db.cursor()

def create_tables_new(conn, cursor):
    print('Create tables new')
    Option(conn, cursor).create_table()
    populate_options(conn, cursor)

    Alert(cursor=cursor).create_table()
    Device(cursor=cursor, conn=conn).create_table()
    DevicePort(cursor=cursor, conn=conn).create_table()
    DeviceWitness(cursor=cursor, conn=conn).create_table()
    ScanPort(cursor=cursor, conn=conn).create_table()
    ScanHost(cursor=cursor, conn=conn).create_table()
    Port(cursor=cursor, conn=conn).create_table()
    EntityMeta(cursor=cursor, conn=conn).create_table()
    DatabaseGrowth(cursor=cursor, conn=conn).create_table()
    SysInfo(cursor=cursor, conn=conn).create_table()


def create_tables(conn, cursor):
    """Create all the applications tables needed."""
    print('Starting create tables')
    Alert(cursor=cursor).create_table()
    Device(cursor=cursor, conn=conn).create_table()
    DevicePort(cursor=cursor, conn=conn).create_table()
    DeviceWitness(cursor=cursor, conn=conn).create_table()
    ScanPort(cursor=cursor, conn=conn).create_table()
    ScanHost(cursor=cursor, conn=conn).create_table()
    Port(cursor=cursor, conn=conn).create_table()
    EntityMeta(cursor=cursor, conn=conn).create_table()
    DatabaseGrowth(cursor=cursor, conn=conn).create_table()
    SysInfo(cursor=cursor, conn=conn).create_table()

def populate_options(conn, cursor):
    """Create options and sets their defaults."""
    o = Option(cursor=cursor, conn=conn).create_table()
    options = Options(cursor=cursor, conn=conn)
    console_password = options.set_defaults()
    return console_password

# End File: lan-nanny/lan_nanny/modules/db.py
