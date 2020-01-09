"""Scan

"""
import argparse
from datetime import datetime, timedelta
import os
import subprocess
import sys

import arrow

from modules import db
from modules.scanning import parse_nmap
from modules.models.device import Device
from modules.models.scan_log import ScanLog
from modules.models.witness import Witness
from modules.models.alert import Alert
from modules.models.alert_event import AlertEvent
from modules.models.port import Port
from modules.collections.devices import Devices
from modules.collections.options import Options

from modules.scanning.scan_ports import ScanPorts
from config import default as config_default

NMAP_SCAN_FILE = "/opt/lan_nanny/hosts.xml"

conn, cursor = db.create_connection(config_default.LAN_NANNY_DB_FILE)


class Scan:

    def __init__(self, args: list=[]):
        self.force_scan = False
        self.new_alerts = []

    def run(self):
        """
        Main entry point to scanning script.

        """
        self._setup()
        print('Running scan number %s' % self.scan_log.id)

        hosts = self.scan()

        # if host scanning is not enabled, hosts returns false
        if type(hosts) == list:
            self._complete_run(len(hosts))
            self.handle_devices(hosts)
            # self.handle_alerts(hosts)
            self.scan_ports(hosts)

    def _setup(self):
        """
        Sets up run log and loads options.

        """
        self.scan_log = ScanLog(conn, cursor)
        self.scan_log.insert_run_start()
        options = Options(conn, cursor)
        self.options = options.get_all_keyed()

    def _complete_run(self, num_devices: int):
        """
        Closes out the run log entry.

        """
        self.scan_log.completed = 1
        self.scan_log.success = 1
        self.scan_log.end_ts = arrow.utcnow().datetime
        self.scan_log.num_devices = num_devices
        self.scan_log.scan_range = self.options['scan-hosts-range'].value
        self.scan_log.save()

    def _abort_run(self):
        """
        Closes out the run log entry.

        """
        self.scan_log.completed = 0
        self.scan_log.success = 0
        self.scan_log.save()

    def scan(self) -> dict:
        """
        Runs NMap scan.

        """
        if not self.force_scan:
            if self.options['scan-hosts-enabled'].value != str(1):
                print('Host scanning disabled. Go to settings to renable.')
                self._abort_run()
                return False
        else:
            print('Forcing scan')


        scan_range = self.options['scan-hosts-range'].value
        # import pdb; pdb.set_trace()
        print('Scan Range: %s' % scan_range)
        # cmd = "nmap -Pn -sn %s -oX %s" % (scan_range, NMAP_SCAN_FILE)
        cmd = "nmap -sP %s -oX %s" % (scan_range, NMAP_SCAN_FILE)
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            self.scan_log.completed = 1
            self.scan_log.success = 0
            self.scan_log.save()
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
            device = Device(conn, cursor)
            device.get_by_mac(host['mac'])
            new = False
            if not device.id:
                new = True
                device.last_seen = scan_time
                host['name'] = host['vendor']
                device.save(raw=host)
            else:
                device.last_seen = scan_time
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
        witness = Witness(conn, cursor)
        witness.device_id = device.id
        witness.run_id = self.scan_log.id
        witness.insert()
        return True

    def handle_alerts(self, hosts: list):
        """
        Handles alerts for devices online or offline.

        """
        print('Running alerts')
        device_collection = Devices(conn, cursor)
        devices = device_collection.with_alerts_on()
        witness = Witness(conn, cursor)

        for device in devices:

            # Device offline check
            if device.alert_offline:
                device_alert = Alert(conn, cursor)
                device_active_offline_alert = device_alert.get_active(device.id, 'offline')


                # If the device is not in the most recent scan, register the alert.
                device_in_scan = witness.get_device_for_scan(device.id, self.scan_log.id)
                if not device_in_scan:
                    device_offline_seconds = (arrow.utcnow().datetime - device.last_seen).seconds
                    timeout_seconds = int(self.options['active-timeout'].value) * 60

                    # if the device has been offline longer than the active time out, alert.
                    if device_offline_seconds > timeout_seconds:
                        self.create_alert(device, 'offline')
                    else:
                        time_til_alert = timeout_seconds - device_offline_seconds
                        print("Device %s is offline, but has not passed active time out yet, %s seconds until alert" % (
                            device, time_til_alert))

                # If the device has an active alert and IS online, we need to set the alert inactive
                else:
                    self.deactivate_alert(device_alert)

            # Device online check
            if device.alert_online == 1:
                device_online = False
                for host in hosts:
                    if device.mac == host['mac']:
                        device_online = True
                        break

                if not device_online:
                    continue

    def create_alert(self, device: Device, alert_type: str):
        """
        Creates an alert unless there's a current active alert for the device and alert type.

        """
        alert = Alert(conn, cursor)
        active_device_alert = alert.get_active(device.id, alert_type)
        if active_device_alert:
            print('Device %s already has an active %s alert.' % (device.name, alert_type))
            self.maintain_active_alert(alert)
            return

        alert.device_id = device.id
        alert.alert_type = alert_type
        alert.acked = 0
        alert.active = 1
        alert.save()

        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'created'
        alert_event.save()

        print('Created %s alert for %s' % (alert_type, device.name))
        self.new_alerts.append(alert)

    def maintain_active_alert(self, alert: Alert):
        """
        """
        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'still_active'
        alert_event.save()

    def deactivate_alert(self, alert: Alert):
        """
        """
        alert.active = False
        alert.save()
        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'deactivate'
        alert_event.save()


    def scan_ports(self, hosts: list):
        """
        Scans ports for hosts which appeared in the current scan, checking first if the device and
        global settings allow for a device to be port scanned.

        """
        print("Running port scans")
        if self.options['scan-hosts-enabled'] != True:
            print('Port Scanning disabled')
            return
        ScanPorts(self.options, conn, cursor).run(hosts)


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
    args = parser.parse_args()
    print(args)
    return args


if __name__ == '__main__':
    # args = parse_args()
    # Scan(args).run()
    Scan().run()

# End File: lan-nanny/lan_nanny/scan.py
