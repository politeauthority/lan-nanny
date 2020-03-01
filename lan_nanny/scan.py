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
from modules.scanning.scan_alerts import ScanAlerts
from modules.scanning.house_keeping import HouseKeeping
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
        self.new_devices = []

    def setup(self):
        """Sets up run log and loads options."""
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
        self.handle_alerts()
        self.handle_house_keeping()

    def hande_hosts(self):
        """Launch host scanning operations."""
        scan_hosts = ScanHosts(self).run()
        if scan_hosts:
            self.hosts, self.new_devices = scan_hosts
        else:
            print('Error scanning hosts, ending scan.')
            exit(1)

    def handle_ports(self):
        """
        Scans ports for hosts which appeared in the current scan, checking first if the device and
        global settings allow for a device to be port scanned.

        """
        ScanPorts(self).run()

    def handle_alerts(self):
        """Handle system alerts."""
        ScanAlerts(self).run()

    def handle_house_keeping(self):
        """Run house keeping operations like database pruning etc."""
        HouseKeeping(self).run()

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
        "-fh",
        "--force-host",
        default=False,
        action='store_true',
        help="")
    parser.add_argument(
        "-fp",
        "--force-port",
        default=False,
        action='store_true',
        help="")
    parser.add_argument(
        "--cron",
        default=False,
        action='store_true',
        help="")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    Scan(args).run()

# End File: lan-nanny/lan_nanny/scan.py
