"""Scan

"""
from datetime import datetime
import subprocess

import arrow

from modules import parse_nmap
from modules import db
from modules.models.devices import Device
from modules.models.run_log import RunLog
from modules.models.witness import Witness
from modules.models.alert import Alert
from modules.collections.devices import Devices
from modules.collections.options import Options

NMAP_SCAN_FILE = "tmp.xml"
NMAP_DB = "lan_nanny.db"

conn, cursor = db.create_connection(NMAP_DB)

class Scan:

    def __init__(self):
        self.new_alerts = []

    def run(self):
        """
        Main entry point to scanning script.

        """
        self._setup()
        print('Running scan number %s' % self.run_log.id)
    
        if self.options['scan-hosts-enabled'] == 0:
            print('Host scanning disabled. Go to settings to renable.')
            self._abort_run()
            exit(0)

        hosts = self.scan()
        self._complete_run()

        self.handle_devices(hosts)

        self.handle_alerts(hosts)

        self.scan_ports(hosts)

    def _setup(self):
        """
        Sets up run log and loads options.

        """
        self.run_log = RunLog(conn, cursor)
        self.run_log.create()
        options = Options(conn, cursor)
        self.options = options.get_all_keyed()

    def _complete_run(self):
        """
        Closes out the run log entry.

        """
        self.run_log.completed = 1
        self.run_log.success = 1
        self.run_log.update()

    def _abort_run(self):
        """
        Closes out the run log entry.

        """
        self.run_log.completed = 0
        self.run_log.success = 0
        self.run_log.update()

    def scan (self) -> dict:
        """
        Runs NMap scan.

        """

        scan_range = self.options['scan-hosts-range']
        print('Scan Range: %s' % scan_range)
        cmd = "nmap -sP %s -oX %s" % (scan_range, NMAP_SCAN_FILE)
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            self.run_log.completed = 1
            self.run_log.success = 0
            self.run_log.update()
            exit(1)
        hosts = parse_nmap.parse_hosts(NMAP_SCAN_FILE)

        return hosts

    def handle_devices(self, hosts: list):
        """
        Handles devices found in NMap scan, creating records for new devices, updating last seen for
        already known devices and saving witness for all found devices.

        """
        print('Found %s devices:' % len(hosts))

        scan_time = arrow.utcnow().datetime
        for host in hosts:
            device = Device(conn, cursor).get_by_mac(host['mac'])
            new = False
            if not device.mac:
                new = True
                device = device.create(scan_time, host)
            else:
                device.last_seen = scan_time
                device.update()

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
        witness = Witness(conn, cursor)
        witness.device_id = device.id
        witness.run_id = self.run_log.id
        witness.witness_ts = scan_time
        witness.create()

        return True

    def handle_alerts(self, hosts: list):
        """
        Handles alerts for devices online or offline.

        """
        print('Running alerts')
        device_collection = Devices(conn, cursor)
        devices = device_collection.get_all()

        witness = Witness(conn, cursor)

        for device in devices:

            # Device offline check
            if device.alert_offline == 1:
                device_in_scan = witness.get_device_for_scan(device.id, self.run_log.id)
                if not device_in_scan:
                    self.create_alert(device, 'offline')

            # Device online check
            if device.alert_online == 1:
                device_online = False
                for host in hosts:
                    if device.mac == host['mac']:
                        device_online = True
                        break

                if not device_online:
                    continue

                last_online_witness = witness.get_device_last_online(device.id)

                # if last_online_witness.witness_ts > 


    def create_alert(self, device: Device, alert_type: str):
        """
        Creates an alert unless there's a current active alert for the device and alert type.

        """
        alert = Alert(conn, cursor)
        active_device_alert = alert.check_active(device.id, alert_type)
        if active_device_alert:
            print('Device %s already has an active %s alert.' % (device.name, alert_type))
            return

        alert.device_id = device.id
        alert.alert_type = 'offline'
        alert.acked = 0
        alert.active = 1
        alert.create()
        print('Created %s alert for %s' % (alert_type, device.name))
        self.new_alerts.append(alert.id)

    def scan_ports(self, hosts: list):
        """
        Scans ports for hosts which appeared in the current scan, checking first if the device and
        global settings allow for a device to be port scanned.

        """
        print("Running port scans")
        port_scan_devices = []

        for host in hosts:
            device = Device(conn, cursor).get_by_mac(host['mac'])

            if device.port_scan == 1:
                port_scan_devices.append(device)

        print(port_scan_devices)
        
        for device in port_scan_devices:
            # cmd = "nmap -p 1-65535 -sV -sS -T4 %s -oX port_scan.xml" % device.ip
            cmd = "nmap %s -oX port_scan.xml" % device.ip
            print(cmd)
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                print('Error running scan, please try again')


if __name__ == '__main__':
    Scan().run()

# End File: lan-nanny/scan.py