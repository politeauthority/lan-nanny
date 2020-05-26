"""ScanHouseKeeping
Runs at the end of scan.py for house keeping operations.

    - Prune data older than the setting `db-prune-days` describes.

"""
from datetime import timedelta
import logging

import arrow

from .. import utils
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.scan_hosts import ScanHosts as CollectScanHosts
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
        self.sys_infos = self.get_sys_infos()

    def get_sys_infos(self) -> dict:
        """Get all system infos keyed on the info's name and return it."""
        collect_sys_infos = SysInfos(self.conn, self.cursor)
        sys_infos = collect_sys_infos.get_all_keyed('name')
        return sys_infos

    def run(self):
        """Main Runner for Scan House Keeping."""
        logging.info('Running House Keeping')
        self.sys_info_start()
        # self.database_growth()
        # self.database_prune()
        # self.get_software_versions()
        self.collect_metrics()

    def sys_info_start(self):
        """Creates the start-date sys info for the Lanny Nanny system, defining when Lan Nanny was
           initially created.
        """
        if 'start-date' in self.sys_infos:
            return True
        info = SysInfo(self.conn, self.cursor)
        info.name = "start-date"
        info.type = "date"
        info.value = arrow.utcnow().datetime
        info.save()
        logging.info('Created Lan Nanny start date sys info')
        return True

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

    def get_software_versions(self):
        """Get software versions of 3rd party utilities Lan Nanny uses."""
        if 'start-date' not in self.sys_infos:
            self.sys_info_start()
        logging.info('\tStarting gather sys info')
        self.get_nmap_version()
        self.get_arp_version()

    def collect_metrics(self) -> bool:
        """Collect metrics of Lan Nanny's performance and usage for local consumption."""
        self.handle_scan_host_run_avg()
        return True

    def sys_info_nmap_version(self):
        """Collect nmap version info."""
        logging.info('Getting nmap version')
        nmap_version = self.get_nmap_version()
        sys_info = SysInfo()
        sys_info.name = 'nmap-version'
        sys_info.type = 'str'
        sys_info.value = nmap_version
        sys_info.save()

    def get_nmap_version(self) -> str:
        """Get the nmap version off the system."""
        if not self._run_job('nmap-version'):
            logging.debug('\tNot running nmap version, too soon.')
            return True
        nmap_v_raw = utils.run_shell('nmap --version')
        nmap_v = nmap_v[nmap_v.find('version') + 8:]
        nmap_v = nmap_v[:nmap_v.find(' ')]
        if 'nmap-version' in self.sys_infos:
            info = self.sys_infos['nmap-version']
        else:
            info = SysInfo(self.conn, self.cursor)
            info.name = "nmap-version"
            info.type = 'str'

        info.update_ts = arrow.utcnow().datetime
        info.value = nmap_v
        info.save()

        return True

    def get_arp_version(self) -> str:
        """Collect arp version info."""
        run = self._run_job('arp-version', 86400)
        if not run:
            logging.debug('\tNot running arp version, too soon.')
            return True

        info = self._create_info('arp-version')
        arp_v = utils.run_shell('arp-scan --version')
        arp_v_str = arp_v[arp_v.find('arp-scan ') + 9: arp_v.find('\n')]
        info.update_ts = arrow.utcnow().datetime
        info.value = arp_v_str
        info.save()
        return True

    def handle_scan_host_run_avg(self):
        """Check if there is a `scan-host-24-avg` sys info, if not try and collect and store an
           average, if there is, check if the value is over 24 hours old and store a new value.
        """
        sec_delta = 86400

        logging.info('\t Handling host scan avg')
        # If the db is so new we dont have a start-date dont run.
        if not 'start-date' in self.sys_infos:
            logging.debug('\t Skipping scan host avg no "start-date"')
            return False

        # If the database is to new dont run.
        start = arrow.get(self.sys_infos['start-date'].value)
        if start > arrow.utcnow().datetime - timedelta(seconds=sec_delta):
            logging.debug('\t Skipping scan host avg "start-date" less than 24 hours')
            return False

        run_new_avg = False
        if 'scan-host-24-avg' not in self.sys_infos:
            new_info = SysInfo(self.conn, self.cursor)
            new_info.name = "scan-host-24-avg"
            new_info.type = 'float'
            # new_info.save()
            self.sys_infos['scan-host-24-avg'] = new_info
            info = new_info
            run_new_avg = True
        else:
            info = self.sys_infos['scan-host-24-avg']
            info.conn = self.conn
            info.cursor = self.cursor

        if info.update_ts > arrow.utcnow().datetime - timedelta(seconds=sec_delta):
            logging.info('\tNot doing new avg, current avg is too new')

        if not run_new_avg:
            logging.debug('\tNot running new scan hosts avg now')
            return True

        collect_scan_hosts = CollectScanHosts(self.conn, self.cursor)
        avg_host_run = collect_scan_hosts.get_avg_runtime(86400)
        info.value = avg_host_run
        info.update_ts = arrow.utcnow().datetime
        info.save()
        logging.info('Saved new 24 hour host scan avg')

    def _run_job(self, job_name, job_timeout=86400):
        """Determine if a job should be run."""
        if not job_name in self.sys_infos:
            return True

        job = self.sys_infos[job_name]

        if job.update_ts < arrow.utcnow().datetime - timedelta(seconds=job_timeout):
            return True

        return False

    def _create_info(self, sys_info_name):
        if sys_info_name in self.sys_infos:
            return self.sys_infos['sys_info_name']
        else:
            info = SysInfo(self.conn, self.cursor)
            info.name = sys_info_name
            info.update_ts = arrow.utcnow().datetime
        return info


# End File: lan_nanny/lan-nanny/modules/scanning/house_keeping.py
