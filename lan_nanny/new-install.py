"""New Install / Upgrade
The new install / upgrade process for Lan Nanny.
This process can be run safely at anytime to setup a new or in place upgrade and existing install.

"""
import logging

from modules import configer
from modules import db
from modules.collections.options import Options as CollectOptions


class InstallUpgrade:

    def run(self):
        """Run the install/upgrader. """
        self.setup_logging()
        # Get the config
        config = configer.get_config()
        # Get the Database
        conn, cursor = self.get_database(config.LAN_NANNY_DB)
        # Create the Database and tables
        db.create_tables_new(conn, cursor)
        logging.info('Creating default options')
        CollectOptions(conn, cursor).set_defaults()

    def setup_logging(self) -> bool:
        """Create the logger."""
        log_level = logging.DEBUG
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]\t%(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=log_level,
            handlers=[logging.StreamHandler()])

    def get_database(self, server):
        """Create the Lan Nanny database if it's not existent, then return the MySql connection."""
        conn, cursor = db.connect_mysql_no_db(server)
        db.create_mysql_database(conn, cursor, server['name'])
        conn, cursor = db.connect_mysql(server)
        logging.info('Database connection successful')
        return conn, cursor


if __name__ == "__main__":
    InstallUpgrade().run()


# End File: lan_nanny/lan-nanny/modules/new-install.py
