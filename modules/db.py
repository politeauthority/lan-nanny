"""DB
Handles the majority of raw database connections.

"""
import sqlite3
from sqlite3 import Error

def create_connection(database_file: str):
    """
    create a database connection to a SQLite database
    """
    conn = None
    try:
        conn = sqlite3.connect(database_file)

    except Error as e:
        print(e)
        exit(1)
    cursor = conn.cursor()
    create_tables(cursor)
    return conn, cursor

def create_tables(cursor: sqlite3.Cursor):
    """
    Creates all the applications tables needed.

    """
    _create_devices(cursor)
    _create_witness(cursor)


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
        name text
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

# End File: lan-nanny/modules/db.py
