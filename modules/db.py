"""DB
Handles the majority of raw database connections.

"""
import sqlite3
from sqlite3 import Error

from .option import Option


def create_connection(database_file: str):
    """
    Create a database connection to a SQLite database

    """
    conn = None
    try:
        conn = sqlite3.connect(database_file)

    except Error as e:
        print(e)
        exit(1)
    cursor = conn.cursor()
    return conn, cursor

def create_tables(cursor: sqlite3.Cursor):
    """
    Creates all the applications tables needed.

    """
    _create_devices(cursor)
    _create_witness(cursor)
    _create_alerts(cursor)
    _create_options(cursor)

def populate_options(conn, cursor: sqlite3.Cursor):
    """
    Creates options and sets their defaults.

    """
    _default_options(conn, cursor, 'timezone', 'America/Denver')
    _default_options(conn, cursor, 'alert-new-device', '1')


def _create_devices(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `devices` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS devices (
        id integer PRIMARY KEY,
        mac text NOT NULL,
        vendor text,
        last_ip text,
        last_seen date,
        first_seen date,
        name text,
        hide integer,
        icon text,
        update_ts date
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def _create_witness(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `witness` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS witness (
        id integer PRIMARY KEY,
        device_id integer NOT NULL,
        witness_ts date
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def _create_alerts(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `alerts` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS alerts (
        id integer PRIMARY KEY,
        device_id integer NOT NULL,
        alert_type integer NOT NULL,
        time_delta integer,
        update_ts date
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def _create_options(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `alerts` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS options (
        id integer PRIMARY KEY,
        name text NOT NULL,
        value text,
        update_ts date
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def _default_options(conn, cursor, option_name, option_value):
    """
    Checks if an option exists in the options table, if not creates it and sets it's default.

    """
    option = Option(conn, cursor)
    option.get_by_name(option_name)
    if not option.name:
        option.name = option_name
        option.value = option_value
        option.create()

# End File: lan-nanny/modules/db.py
