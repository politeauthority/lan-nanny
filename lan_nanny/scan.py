"""Scan

"""
import argparse

from modules import db
from modules.collections.options import Options
from modules.scanning.scan_ports import ScanPorts
from modules.scanning.scan_hosts import ScanHosts
from config import default as config_default

TMP_DIR = "/opt/lan_nanny/"

conn, cursor = db.create_connection(config_default.LAN_NANNY_DB_FILE)


class Scan:

    def __init__(self, args):
        self.conn = conn
        self.cursor = cursor
        self.args = args
        self.force_scan = False
        self.trigger = 'manual'
        self.new_alerts = []
        self.hosts = []

    def setup(self):
        """
        Sets up run log and loads options.

        """
        options = Options(conn, cursor)
        self.options = options.get_all_keyed()
        self.tmp_dir = TMP_DIR
        if self.args.cron:
            self.trigger = 'cron'

    def run(self):
        """
        Main entry point to scanning script.

        """
        self.setup()
        self.hande_hosts()
        self.handle_ports()

    def hande_hosts(self):
        self.hosts = ScanHosts(self).run()

    def handle_ports(self):
        """
        Scans ports for hosts which appeared in the current scan, checking first if the device and
        global settings allow for a device to be port scanned.

        """
        print("Running port scans")
        if not self.hosts:
            print('No hosts found in last scan, skipping port scan')
            return False
        if self.options['scan-ports-enabled'].value != True:
            print('Port Scanning disabled')
            return False
        ScanPorts(self).run()


def parse_args():
    """
    Parses args from the cli with ArgumentParser
    :returns: Parsed arguments
    :rtype: <Namespace> obj
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--force-scan",
        default=False,
        action='store_true',
        help="")
    parser.add_argument(
        "--cron",
        default=False,
        action='store_true',
        help="")
    args = parser.parse_args()
    print(args)
    return args


if __name__ == '__main__':
    args = parse_args()
    Scan(args).run()

# End File: lan-nanny/lan_nanny/scan.py
