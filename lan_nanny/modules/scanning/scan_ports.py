"""Scan Ports

"""
import os
import subprocess

import arrow

from . import parse_nmap
from ..collections.devices import Devices
from ..models.device import Device
from ..models.port import Port
from ..models.scan_log import ScanLog


class ScanPorts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.tmp_dir = scan.tmp_dir
        self.options = scan.options
        self.hosts = scan.hosts
        self.trigger = scan.trigger

    def run(self):
        """
        Main Runner for Scan Port.

        """
        port_scan_candidates = self.get_port_scan_candidates()

        print("Port Scanning %s devices" % len(port_scan_candidates))

        if not port_scan_candidates:
            print('No devices ready for port scan, skipping.')
            return

        for device in port_scan_candidates:
            device_og_port_scan = device.last_port_scan
            device.conn = self.conn
            device.cursor = self.cursor

            # so we dont overrun, mark this as the last port scan now. @todo this should be
            # done better
            device.last_port_scan = arrow.utcnow().datetime
            device.save()

            ports = self.scan_ports(device)

            if not ports:
                device.last_port_scan = device_og_port_scan
                device.save()
                print('Port scan failed for %s, will try again soon.' % device)
                continue

            self.handle_ports(device, ports)

            end = arrow.utcnow()

            print('Saved port scan for %s found %s open ports' % (
                device,
                '@todo'))
            device.last_port_scan = arrow.utcnow().datetime
            device.flagged_for_scan = 0
            device.save()

    def get_port_scan_candidates(self):
        """
        Get the device candidates for port scanning that appeared in the last host scan and are
        ready for a port scan, also limit the number of hosts to port scan based on the setting.

        """
        devices = Devices(self.conn, self.cursor).for_port_scanning()
        port_scan_devices = []

        for host in self.hosts:
            for d in devices:
                if d.mac == host['mac']:
                    port_scan_devices.append(d)
                    continue

        print('Found %s Port Scan candidates' % len(port_scan_devices))

        limit = int(self.options['scan-ports-per-run'].value)
        if len(port_scan_devices) > limit:
            if limit == 1:
                port_scan_devices = [port_scan_devices[0]]
            else:
                port_scan_devices = port_scan_devices[0:limit]

            print("Limiting port scan to %s devices because of app setting" % limit)

        return port_scan_devices

    def scan_ports(self, device: Device) -> list:
        """
        Run and manage a NMAP port scan for a single device to derive port data and returning those
        ports in a list of dicts.

        """
        scan_log = ScanLog(self.conn, self.cursor)
        scan_log.trigger = self.trigger
        scan_log.command = "nmap %s --host-timeout 120 --max-retries 5" % device.ip
        scan_log.insert_run_start('port')

        port_scan_file = os.path.join(self.tmp_dir, "port_scan_%s.xml" % device.id)
        cmd = "%s -oX %s" % (scan_log.command, port_scan_file)
        print('Running port scan for %s' % device)
        print('\tCmd: %s' % scan_log.command)
        try:
            subprocess.check_output(cmd, shell=True)
            scan_log.success = True
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            scan_log.success = False
            scan_log.end_run()
            return False

        ports = parse_nmap.parse_xml(port_scan_file, 'ports')

        # scan_log.units = len(ports)
        scan_log.completed = True
        scan_log.end_run()
        os.remove(port_scan_file)
        return ports

    def handle_ports(self, device: Device, ports: list):
        """

        """
        if not ports:
            print('Device offline or no ports for %s' % device)
            return

        num_ports = 0
        for port in ports:
            device_port = Port(self.conn, self.cursor)
            device_port.get_by_device_port_protocol(device.id, port['number'], port['protocol'])
            device_port.device_id = device.id
            device_port.port = port['number']
            device_port.protocol = port['protocol']
            device_port.service_name = port['service']
            device_port.status = 'open'
            device_port.last_seen = arrow.utcnow().datetime
            device_port.save()
            num_ports += 1

        print('Device %s has %s ports open' % (device, num_ports))
        # if device.ports:
        #     import ipdb; ipdb.set_trace()
        # for device_port in device.ports:
        #     if device_port.status == 'closed':
        #         continue
        #     device_port_closed = True
        #     for scan_ports in ports:
        #         if device_port.port == scan_port['number']:
        #             device_port_closed = False
        #     if device_port_closed:
        #         device_port


# End File: lan_nanny/nanny-nanny/modules/scan_ports.py
