"""Database handler.
Handles the raw database connections, and database initialization of tables and required values.

"""
import logging
import sqlite3

from flask import g
import mysql.connector
from mysql.connector import Error as MySqlError

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


def connect_mysql(server: dict):
    """Connect to MySql server and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['host'],
            user=server['user'],
            password=server['pass'],
            database=server['name'])
        if connection.is_connected():
            db_info = connection.get_server_info()
            logging.debug(db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            logging.debug(record)
        return connection, cursor
    except MySqlError as e:
        logging.error("Error while connecting to MySQL", e)
        exit(1)


def connect_mysql_no_db(server: dict):
    """Connect to MySql server, without specifying a database, and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['host'],
            user=server['user'],
            password=server['pass'])
        if connection.is_connected():
            db_info = connection.get_server_info()
            logging.debug(db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            logging.debug(record)
        return connection, cursor
    except MySqlError as e:
        logging.error("Error while connecting to MySQL", e)
        exit(1)


def create_mysql_database(conn, cursor, db_name: str):
    """Create the MySQL database."""
    sql = """CREATE DATABASE IF NOT EXISTS %s""" % db_name
    cursor.execute(sql)
    print('Created database: %s' % db_name)
    return True


def get_db_flask(database_file: str):
    """Create a database connection to a SQLite database for the flask web environment."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_file)
    return db, db.cursor()


def create_tables_new(conn, cursor):
    logging.info("Creating tables if they don't exist")
    Option(conn, cursor).create_table()
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

# def populate_options(conn, cursor):
#     """Create options and sets their defaults."""
#     o = Option(cursor=cursor, conn=conn).create_table()
#     options = Options(cursor=cursor, conn=conn)
#     console_password = options.set_defaults()
#     return console_password


# End File: lan-nanny/lan_nanny/modules/db.py
