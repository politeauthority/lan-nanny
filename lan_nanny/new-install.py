"""
"""

import os

from modules import configer
from modules import db


def run():
    config = configer.get_config()
    conn, cursor = get_database(config.LAN_NANNY_DB)
    import ipdb; ipdb.set_trace()

    db.create_tables_new(conn, cursor)

def get_database(server):
    """Create the Lan Nanny database if it's not existent."""
    conn, cursor = db.connect_mysql_no_db(server)
    db.create_mysql_database(conn, cursor, server['name'])
    conn, cursor = db.connect_mysql(server)
    return conn, cursor


if __name__ == "__main__":
    run()