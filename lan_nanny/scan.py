"""Entry point to all scan operations and other tasks that need to be run on a regular schedule.

    Scans hosts on network
    Scans ports for a given host
    Runs house keeping operations.

    This script must be run with sudo privileges for network scanning to work properly.

"""
import argparse
import os

from modules import db
from modules.collections.options import Options
from modules.scanning.scan_ports import ScanPorts
from modules.scanning.scan_hosts import ScanHosts
from modules.scanning.scan_house_keeping import ScanHouseKeeping
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
        self.db_file_loc = config_default.LAN_NANNY_DB_FILE
        self.new_alerts = []
        self.hosts = []

    def setup(self):
        """
        Sets up run log and loads options.

        """
        self.prompt_sudo()
        options = Options(conn, cursor)
        self.options = options.get_all_keyed()
        self.tmp_dir = TMP_DIR
        if self.args.cron:
            self.trigger = 'cron'

    def run(self):
        """Main entry point to scanning script."""
        self.setup()
        self.hande_hosts()
        self.handle_ports()
        self.handle_house_keeping()

    def hande_hosts(self):
        """Launch host scanning operations."""
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

    def handle_house_keeping(self):
        """Run house keeping operations like database pruning etc."""
        ScanHouseKeeping(self).run()

    def prompt_sudo(self):
        """Make sure the script is being run as sudo, or scanning will not work."""
        ret = 0
        if os.geteuid() != 0:
            msg = "[sudo] password for %u:"
            ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
        return ret

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
