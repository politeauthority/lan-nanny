"""ScanHouseKeeping
Runs at the end of scan.py for house keeping operations.

    - Prune data older than the setting `db-prune-days` describes.

"""
from datetime import timedelta
import logging
import os

import arrow

from ..collections.device_witnesses import DeviceWitnesses
from ..models.database_growth import DatabaseGrowth


class ScanHouseKeeping:

    def __init__(self, scan):
        """Set base class vars."""
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.tmp_dir = scan.tmp_dir
        self.options = scan.options
        self.db_file_loc = scan.db_file_loc

    def run(self):
        """Main Runner for Scan House Keeping."""
        self.database_growth()
        self.database_prune()

    def database_growth(self):
        """Record the current database size once an hour."""
        last_growth = DatabaseGrowth(self.conn, self.cursor)
        last_growth.get_last()

        create_new = False
        if not last_growth.id:
            create_new = True
        else:
            time_for_new_snapshot = last_growth.created_ts + timedelta(minutes=15) < \
                arrow.utcnow().datetime
            if time_for_new_snapshot:
                create_new = True

        if not create_new:
            logging.debug('Not creating new database growth record.')
            return

        print('Creating new DB Growth')
        new_growth = DatabaseGrowth(self.conn, self.cursor)
        new_growth.size = os.path.getsize(self.db_file_loc)
        new_growth.save()

    def database_prune(self):
        """Prunes database records after they are older the `db-prune-days` option value."""
        if self.options['db-prune-days'].value:
            days = int(self.options['db-prune-days'].value)
        else:
            return
        print('Running prune of data older than %s days' % days)

        # @todo: Add scan host and scan port model prunes.
        DeviceWitnesses(self.conn, self.cursor).prune(days)


# End File: lan_nanny/nanny-nanny/modules/scanning/scan_house_keeping.py
