"""
"""
from importlib import import_module
import os

from modules import db


def run():
    config = get_config()
    conn, cursor = db.connect_mysql_no_db(config.LAN_NANNY_DB)
    db.create_mysql_database(conn, cursor)

    conn, cursor = db.connect_mysql(config.LAN_NANNY_DB)
    db.create_tables_new(conn, cursor)


def get_config():
    """Get the application configs."""
    if os.environ.get('LAN_NANNY_CONFIG'):
        config_file = os.environ.get('LAN_NANNY_CONFIG')
        configs = import_module('config.%s' % config_file)
        # imported_module = import_module('.config.%s' % config)
        print('Using config: %s' % os.environ.get('LAN_NANNY_CONFIG') )
    else:
        print('Using config: default')
        configs = import_module('config.default')
    return configs


if __name__ == "__main__":
    run()