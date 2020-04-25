"""ScanHouseKeeping
Runs at the end of scan.py for house keeping operations.

    - Prune data older than the setting `db-prune-days` describes.

"""
from datetime import timedelta
import logging
import os

import arrow

from .. import utils
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.sys_infos import SysInfos
from ..models.database_growth import DatabaseGrowth
from ..models.sys_info import SysInfo


class HouseKeeping:

    def __init__(self, scan):
        """Set base class vars."""
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.tmp_dir = scan.tmp_dir
        self.options = scan.options

    def run(self):
        """Main Runner for Scan House Keeping."""
        logging.info('Running House Keeping')
        # self.database_growth()
        # self.database_prune()
        self.gather_sys_info()

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

        logging.info('Creating new DB Growth')
        new_growth = DatabaseGrowth(self.conn, self.cursor)
        new_growth.size = None
        new_growth.save()

    def database_prune(self):
        """Prunes database records after they are older the `db-prune-days` option value."""
        if self.options['db-prune-days'].value:
            days = int(self.options['db-prune-days'].value)
        else:
            return
        logging.info('Running prune of data older than %s days' % days)

        # @todo: Add scan host and scan port model prunes.
        DeviceWitnesses(self.conn, self.cursor).prune(days)

    def gather_sys_info(self):
        sys_infos = SysInfos(self.conn, self.cursor).get_all_keyed()
        if 'start-date' not in sys_infos:
            self.sys_info_start()
        # if 'nmap-version' not in sys_infos:
        #     self.sys_info_nmap_version()

    def sys_info_start(self):
        info = SysInfo(self.conn, self.cursor)
        info.name = "start-date"
        info.type = "date"
        info.value = arrow.utcnow().datetime
        info.save()
        logging.info('Created Lan Nanny start date sys info')
        return True

    def sys_info_nmap_version(self):
        nmap_version = self._get_nmap_version()
        sys_info = SysInfo()
        sys_info.name = 'nmap-version'
        sys_info.type = 'str'
        sys_info.value = nmap_version
        sys_info.save()

    def _get_nmap_version(self) -> str:
        nmap_v = utils.run_shell('nmap --version')
        nmap_v = nmap_v[nmap_v.find('version') + 8:]
        nmap_v = nmap_v[:nmap_v.find(' ')]

        return nmap_v


# End File: lan_nanny/lan-nanny/modules/scanning/house_keeping.py
