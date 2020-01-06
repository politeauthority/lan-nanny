import os
import subprocess

import arrow

from ..collections.devices import Devices
from ..models.port import Port
from . import parse_nmap


class ScanPorts:

    def __init__(self, options, conn, cursor):
        self.options = options
        self.conn = conn
        self.cursor = cursor

    def run(self, hosts_online: list):
        devices = Devices(self.conn, self.cursor).for_port_scanning(limit=1)

        port_scan_devices = []
        port_scan_device_macs = []

        for host in hosts_online:
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
                devices = devices[0:limit-1]

            print("Limiting port scan to %s devices" % limit)

        for device in port_scan_devices:
            start = arrow.utcnow()
            device.conn = self.conn
            device.cursor = self.cursor

            # so we dont overrun, mark this as the last port scan now. @todo this should be
            # done better
            device.last_port_scan = arrow.utcnow().datetime
            device.save()

            port_scan_file = "port_scan_%s.xml" % device.id
            cmd = "nmap %s -oX %s" % (device.ip, port_scan_file)
            print('Running port scan for %s' % device)
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                print('Error running scan, please try again')
                return

            ports = parse_nmap.parse_ports(port_scan_file)

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

            device.conn = self.conn
            device.cursor = self.cursor

            os.remove(port_scan_file)
            end = arrow.utcnow()

            scan_time = end - start
            print('Saved port scan for %s found %s open ports, took %s' % (device, num_ports, scan_time))