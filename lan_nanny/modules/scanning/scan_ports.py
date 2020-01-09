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
        self.options = scan.options
        self.hosts = scan.hosts

    def run(self):
        devices = Devices(self.conn, self.cursor).for_port_scanning(limit=1)

        port_scan_devices = []

        for host in self.hosts:
            for d in devices:
                if d.mac == host['mac']:
                    port_scan_devices.append(d)
                    continue

        print("Found %s devices for port scan" % len(port_scan_devices))

        if not devices:
            print('No devices ready for port scan, skipping.')
            return

        limit = 3
        if len(devices) > limit:
            limit = 1
            if limit == 1:
                devices = [devices[0]]
            else:
                devices = devices[0:limit - 1]

            print("Limiting port scan to %s devices" % limit)

        for device in port_scan_devices:
            start = arrow.utcnow()
            device.conn = self.conn
            device.cursor = self.cursor

            # so we dont overrun, mark this as the last port scan now. @todo this should be
            # done better
            device.last_port_scan = arrow.utcnow().datetime
            device.save()

            ports = self.scan_ports(device)

            self.handle_ports(device, ports)

            end = arrow.utcnow()

            scan_time = end - start
            print('Saved port scan for %s found %s open ports, took %s' % (
                device,
                num_ports,
                scan_time))

    def scan_ports(self, device: Device):
        """
        """
        scan_log = ScanLog(self.conn, self.cursor)
        scan_log.command = "nmap %s" % device.ip
        scan_log.insert_run_start('port')

        port_scan_file = os.path.join(self.temp_dir, "port_scan_%s.xml" % device.id)
        cmd = "%s -oX %s" % (self.scan_log.command, port_scan_file)
        print('Running port scan for %s' % device)
        try:
            subprocess.check_output(cmd, shell=True)
            scan_log.success = True
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            scan_log.success = False
            scan_log.end_run()
            return False

        ports = parse_nmap.parse_ports(port_scan_file)

        scan_log.units = len(ports)
        scan_log.completed = True
        scan_log.end_run()
        os.remove(port_scan_file)
        return ports

    def handle_ports():
        if not ports:
            print('Device offline or no ports for %s' % device)
            device.last_port_scan = arrow.utcnow().datetime
            device.save()
            return

        num_ports = 0
        for port in ports:
            device_port = Port(self.conn, self.cursor)
            device_port.device_id = device.id
            device_port.port = port['number']
            device_port.protocol = port['protocol']
            device_port.service_name = port['service']
            device_port.get_by_device_port_protocol()
            device_port.save()
            num_ports += 1

# End File: lan_nanny/nanny-nanny/modules/scan_ports.py
