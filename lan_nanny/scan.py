"""Entry point to all scan operations and other tasks that need to be run on a regular schedule.

    Scans hosts on network
    Scans ports for a given host
    Runs house keeping operations.

    This script must be run with sudo privileges for network scanning to work properly.

"""
import argparse
from importlib import import_module
import logging
import logging.config
import subprocess
import sys
import os

from werkzeug.security import generate_password_hash

from modules import db
from modules.collections.options import Options
from modules.models.option import Option
from modules.scanning.scan_ports import ScanPorts
from modules.scanning.scan_hosts import ScanHosts
from modules.scanning.scan_alerts import ScanAlerts
# from modules.scanning.house_keeping import HouseKeeping


class Scan:

    def __init__(self, configs, args):
        """
        :param configs: LanNanny application configs.
        :param args: CLI arguments
        """
        self.conn, self.cursor = db.connect_mysql(configs.LAN_NANNY_DB)
        self.args = args
        self.force_scan = False
        self.trigger = 'manual'
        self.new_alerts = []
        self.hosts = []
        self.new_devices = []
        self.config = configs

    def setup(self):
        """Sets up run log and loads options."""
        self.setup_logging()
        self.prompt_sudo()
        options = Options(self.conn, self.cursor)
        self.options = options.get_all_keyed('name')
        self.tmp_dir = self.config.LAN_NANNY_TMP_DIR
        if self.args.cron:
            self.trigger = 'cron'
        logging.info('Scan triggered by %s' % self.trigger)

    def run(self):
        """Main entry point to scanning script."""
        self.setup()
        self.handle_cli()
        self.hande_hosts()
        self.handle_ports()
        self.handle_alerts()
        # self.handle_house_keeping()

    def handle_cli(self) -> bool:
        """Handle one off/simple CLI requests"""
        self._cli_change_password()

    def hande_hosts(self) -> bool:
        """Launch host scanning operations."""
        scan_hosts = ScanHosts(self).run()
        if scan_hosts:
            self.hosts, self.new_devices, self.scan_hosts_log = scan_hosts
        else:
            logging.error('Error scanning hosts, ending scan.')
            exit(1)

        # try:
        #     scan_hosts = ScanHosts(self).run()
        #     if scan_hosts:
        #         self.hosts, self.new_devices, self.scan_hosts_log = scan_hosts
        #     else:
        #         logging.error('Error scanning hosts, ending scan.')
        #         exit(1)
        # except:
        #     logging.error('Error running host scan.')
        #     exit(1)
        #     return False

        return True

    def handle_ports(self):
        """Scans ports for hosts which appeared in the current scan, checking first if the device and
           global settings allow for a device to be port scanned.
        """
        try:
            ScanPorts(self).run()
        except:
            logging.error('Scan Ports failed')

    def handle_alerts(self):
        """Handle system alerts."""
        ScanAlerts(self).run()

    def handle_house_keeping(self):
        """Run house keeping operations like database pruning etc."""
        logging.info('House keeping is broken, skipping.')
        # HouseKeeping(self).run()

    def _cli_change_password(self):
        if not self.args.password_reset:
            return True
        print('Are you sure you want to reset the console password?')
        verify = input('Verify: (only "y" will continue) ')

        if verify != 'y':
            print('Not changing password')
            exit(0)
        new_password = input('New Password: ')
        new_password2 = input('New Password Again: ')

        if new_password != new_password2:
            print('Passwords do not match')
            exit(1)
        print('Changing console password')
        new_pass = generate_password_hash(new_password, "sha256")
        pass_option = Option(self.conn, self.cursor)
        pass_option.get_by_name("console-password")
        pass_option.value = new_pass
        pass_option.update()
        print('Saved new console password')
        exit()

    def setup_logging(self) -> bool:
        """Create the logger."""
        log_level = logging.DEBUG
        if self.args.verbose:
            log_level = logging.DEBUG
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]\t%(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=log_level,
            handlers=[logging.StreamHandler()])

        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Logging enabled - debug')
        return True

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
        "--password-reset",
        default=False,
        action='store_true',
        help="")
    parser.add_argument(
        "--cron",
        default=False,
        action='store_true',
        help="")
    parser.add_argument(
        "--config",
        default=False,
        help="")
    parser.add_argument(
        "--verbose",
        default=False,
        action='store_true',
        help="Run at debug logging level")
    args = parser.parse_args()
    return args


def get_config(args):
    """Get the application configs."""

    # Check if the --config CLI arg was used.
    if args.config:
        print('Using config: %s' % args.config)
        configs = import_module('config.%s' % args.config)

    # Check if the ENV var is set
    elif os.environ.get('LAN_NANNY_CONFIG'):
        config_file = os.environ.get('LAN_NANNY_CONFIG')
        configs = import_module('config.%s' % config_file)
        print('Using config: %s' % os.environ.get('LAN_NANNY_CONFIG'))

    # Use default configs
    else:
        print('Using config: default')
        configs = import_module('config.default')
    return configs


if __name__ == '__main__':
    args = parse_args()
    configs = get_config(args)
    Scan(configs, args).run()


# End File: lan-nanny/lan_nanny/scan.py
