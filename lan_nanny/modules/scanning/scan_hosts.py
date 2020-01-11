"""Scan Hosts - Runs host NMAP scans and saves the results.

"""
from datetime import datetime
import os
import subprocess

import arrow
from . import parse_nmap
from ..models.scan_log import ScanLog
from ..models.device import Device
from ..models.witness import Witness


class ScanHosts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.tmp_dir = scan.tmp_dir
        self.scan_file = os.path.join(self.tmp_dir, 'host-scan.xml')
        self.trigger = scan.trigger

    def run(self) -> list:
        """
        Runs NMap scan.

        """
        self.setup()

        if self.options['scan-hosts-enabled'].value != True:
            print('Host scanning disabled. Go to settings to renable.')
            self._abort_run()
            return []

        self.hosts = self.scan()
        self._complete_run()
        self.handle_devices()

        return self.hosts

    def setup(self):
        """
        """
        self.scan_log = ScanLog(self.conn, self.cursor)
        self.scan_log.trigger = self.trigger
        self.scan_log.insert_run_start('host')

    def scan(self):
        """
        """
        scan_range = self.options['scan-hosts-range'].value
        print('Scan Range: %s' % scan_range)
        self.scan_log.command = "nmap -sP %s" % scan_range
        cmd = "nmap -sP %s -oX %s" % (scan_range, self.scan_file)
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            self.scan_log.completed = True
            self.scan_log.success = True
            self.scan_log.save()
            exit(1)
        hosts = parse_nmap.parse_xml(self.scan_file, 'hosts')
        return hosts

    def handle_devices(self):
        """
        Handles devices found in NMap scan, creating records for new devices, updating last seen for
        already known devices and saving witness for all found devices.

        """
        print('Found %s devices:' % len(self.hosts))

        scan_time = arrow.utcnow().datetime
        for host in self.hosts:

            device = Device(self.conn, self.cursor)
            device.get_by_mac(host['mac'])
            new = False
            if not device.id:
                new = True
                device.first_seen = scan_time
                device.name = host['vendor']
                device.mac = host['mac']
                if self.options['scan-ports-default'].value:
                    device.port_scan = True
            device.last_seen = scan_time
            device.ip = host['ip']
            device.vendor = host['vendor']
            print(device.first_seen)
            device.save()

            new_device_str = ""
            if new:
                new_device_str = "\t- New Device"
            if device.name:
                print('\t%s - %s%s' % (device.name, device.ip, new_device_str))
            elif device.vendor:
                print('\t%s - %s%s' % (device.vendor, device.ip, new_device_str))
            else:
                print('\t%s - %s%s' % (device.mac, device.ip, new_device_str))

            self.save_witness(device, scan_time)

    def save_witness(self, device: Device, scan_time: datetime) -> bool:
        """
        Creates a record in the `witness` table of the devices id and scan time.

        """
        witness = Witness(self.conn, self.cursor)
        witness.device_id = device.id
        witness.run_id = self.scan_log.id
        witness.insert()
        return True

    def _complete_run(self):
        """
        Closes out the run log entry.

        """
        self.scan_log.completed = 1
        self.scan_log.success = 1
        self.scan_log.end_ts = arrow.utcnow().datetime
        # self.scan_log.num_devices = len(self.hosts)
        self.scan_log.scan_range = self.options['scan-hosts-range'].value
        self.scan_log.save()

    def _abort_run(self):
        """
        Closes out the run log entry.

        """
        self.scan_log.completed = 0
        self.scan_log.success = 0
        self.scan_log.save()

# End File: lan-nanny/lan_nanny/modules/scanning/scan_hosts.py