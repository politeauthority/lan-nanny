"""DB
Handles the majority of raw database connections.

"""
import sqlite3
from sqlite3 import Error

from flask import g

from .models.option import Option
from .models.alert import Alert
from .models.device import Device
from .models.alert_event import AlertEvent
from .models.run_log import RunLog
from .models.witness import Witness
from .models.port import Port


def create_connection(database_file: str):
    """
    Create a database connection to a SQLite database.

    """
    conn = None
    try:
        conn = sqlite3.connect(database_file)

    except Error as e:
        print(e)
        exit(1)
    cursor = conn.cursor()
    return conn, cursor


def get_db_flask(database_file: str):
    """
    Create a database connection to a SQLite database for the flask web environment.

    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_file)
    return db, db.cursor()


def create_tables(conn, cursor):
    """
    Creates all the applications tables needed.

    """
    print('Starting create tables')
    Alert(cursor=cursor).create_table()
    AlertEvent(cursor=cursor).create_table()
    Device(cursor=cursor, conn=conn).create_table()
    Option(cursor=cursor, conn=conn).create_table()
    populate_options(conn, cursor)
    RunLog(cursor=cursor, conn=conn).create_table()
    Witness(cursor=cursor, conn=conn).create_table()
    Port(cursor=cursor, conn=conn).create_table()


def populate_options(conn, cursor: sqlite3.Cursor):
    """
    Creates options and sets their defaults.

    """
    _set_default_options(conn, cursor, 'timezone', 'America/Denver', 'str')
    _set_default_options(conn, cursor, 'alert-new-device', '1', 'bool')
    _set_default_options(conn, cursor, 'active-timeout', '8', 'int')
    _set_default_options(conn, cursor, 'scan-hosts-enabled', '1', 'bool')
    _set_default_options(conn, cursor, 'scan-hosts-ports-default', '0', 'bool')
    _set_default_options(conn, cursor, 'scan-hosts-range', '192.168.50.1-255', 'str')


def _set_default_options(conn, cursor, option_name: str, option_value, option_type):
    """
    Checks if an option exists in the options table, if not creates it and sets it's default.

    """
    option = Option(conn, cursor)
    option.get_by_name(option_name)
    if not option.name:
        option.name = option_name
        option.value = option_value
        option.type = option_type
    else:
        option.value = option_value
    option.save()
    # print('Made opts: %s %s' % (option_name, option_value))


def _create_run_log(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `run_log` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS run_log (
        id integer PRIMARY KEY,
        start_ts date NOT NULL,
        end_ts date,
        elapsed_time text,
        completed integer,
        success integer,
        num_devices integer,
        scan_range text
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False

# End File: lan-nanny/modules/db.py
