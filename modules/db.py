"""DB
Handles the majority of raw database connections.

"""
import sqlite3
from sqlite3 import Error

from flask import g

from .models.option import Option
from .models.alert import Alert
from .models.alert_event import AlertEvent


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
    AlertEvent(cursor=cursor).create_table()
    Alert(cursor=cursor).create_table()
    _create_devices(cursor)
    _create_witness(cursor)
    _create_ports(cursor)
    _create_options(cursor)
    _create_run_log(cursor)


def populate_options(conn, cursor: sqlite3.Cursor):
    """
    Creates options and sets their defaults.

    """
    _set_default_options(conn, cursor, 'timezone', 'America/Denver')
    _set_default_options(conn, cursor, 'alert-new-device', '1')
    _set_default_options(conn, cursor, 'active-timeout', '8')
    _set_default_options(conn, cursor, 'scan-hosts-enabled', '1')
    _set_default_options(conn, cursor, 'scan-hosts-ports-default', '0')
    _set_default_options(conn, cursor, 'scan-hosts-range', '192.168.1.1-255')


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
        favorite integer DEFAULT 0,
        icon text,
        alert_online integer DEFAULT 0,
        alert_offline integer DEFAULT 0,
        alert_delta integer,
        port_scan integer,
        last_port_scan date,
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
        run_id integer,
        witness_ts date
    );
    """
    try:
        cursor.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def _create_ports(cursor: sqlite3.Cursor) -> bool:
    """
    Creates the `ports` table.

    """
    sql = """
    CREATE TABLE IF NOT EXISTS ports (
        id integer PRIMARY KEY,
        device_id integer NOT NULL,
        port text,
        last_seen date,
        status text,
        service_name text,
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


def _set_default_options(conn, cursor, option_name, option_value):
    """
    Checks if an option exists in the options table, if not creates it and sets it's default.

    """
    option = Option(conn, cursor)
    option.get_by_name(option_name)
    if not option.name:
        option.name = option_name
        option.value = option_value
        option.create()


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
