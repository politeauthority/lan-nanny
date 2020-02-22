"""ScanPorts controls device port scanning efforts.

"""
from datetime import timedelta
import logging
import os
import subprocess
import time

import arrow

from . import parse_nmap
from ..collections.devices import Devices
from ..collections.device_ports import DevicePorts
from ..models.device import Device
from ..models.device_port import DevicePort
from ..models.port import Port
from ..models.scan_port import ScanPort

class ScanPorts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.tmp_dir = scan.tmp_dir
        self.options = scan.options
        self.hosts = scan.hosts
        self.trigger = scan.trigger

    def run(self):
        """ Main Runner for Scan Port."""
        port_scan_devices = self.get_port_scan_candidates()

        if not port_scan_devices:
            print('\tNo devices ready for port scan, skipping.')
            return

        print('\tStarting Device Port Scans for %s devices' % len(port_scan_devices))
        for device in port_scan_devices:
            self.handle_device_port_scan(device)

        return True

    def get_port_scan_candidates(self) -> list:
        """ Gets devices present in last scan which meet port scanning criteria."""
        host_port_scan_interval_mins = int(self.options['scan-ports-interval'].value)
        host_port_scan_timeout = arrow.utcnow().datetime - timedelta(minutes=host_port_scan_interval_mins)
        port_scan_devices = []
        for host in self.hosts:

            # Remove devices that dont allow port scanning.
            if not host['device'].port_scan:
                logging.info('%s does not have port scanning enabled' % host['device'])
                continue

            # Remove devices that have been port scanned in x minutes.
            if not host['device'].last_port_scan or \
                (host['device'].last_port_scan > host_port_scan_timeout):
                logging.info('%s has been scanned in the last %s minutes' % (
                    host['device'],
                    host_port_scan_interval_mins))
                continue

            port_scan_devices.append(host['device'])
        
        limit = int(self.options['scan-ports-per-run'].value)
        if len(port_scan_devices) > limit:
            port_scan_devices = port_scan_devices[0:limit]
            print("Limiting port scan to %s devices" % limit)

        return port_scan_devices

    def handle_device_port_scan(self, device: Device) -> True:
        """Run device port scan and related processes for a single device."""
        device_og_port_scan = device.last_port_scan
        device.conn = self.conn
        device.cursor = self.cursor

        # Lock the device from other scan processes.
        device.port_scan_lock = True
        device.save()

        device_port_scan = self.scan_ports_cmd(device)
        device.last_port_scan_id = device_port_scan['scan_port_log'].id

        # Release device port scan lock.
        device.port_scan_lock = False
        device.save()

        # if port scanning failed for any reason.
        if not device_port_scan['ports']:

            print('Port scan failed for %s, will try again soon.' % device)
            return False

        self.handle_ports(device, device_port_scan['ports'])

        end = arrow.utcnow()

        print('Saved port scan for %s found %s open ports' % (
            device,
            '@todo'))
        device.last_port_scan = arrow.utcnow().datetime
        device.flagged_for_scan = 0
        device.save()
        return True

    def scan_ports_cmd(self, device: Device) -> list:
        """Run and manages an NMAP port scan for a single device to derive port data and returning
           those ports in a list of dicts.
        """
        scan = self.create_device_port_scan_log(device)
        start = time.time()
        port_scan_file = os.path.join(self.tmp_dir, "port_scan_%s.xml" % device.id)
        cmd = "%s -oX %s" % (scan.command, port_scan_file)
        print('\tRunning port scan for %s' % device)
        print('\tCmd: %s' % scan.command)

        try:
            subprocess.check_output(cmd, shell=True)
            scan.success = True
        except subprocess.CalledProcessError:
            print('Error running scan, please try again')
            end = time.time()
            scan.elapsed_time = end - start
            self._complete_run_error(scan)
            return False
        end = time.time()
        scan.elapsed_time = end - start
        scan.end_run()

        ports = parse_nmap.parse_xml(port_scan_file, 'ports')
        # scan.units = len(ports)
        os.remove(port_scan_file)
        ret = {
            'ports': ports,
            'scan_port_log': scan,
        }
        return ret

    def create_device_port_scan_log(self, device: Device) -> bool:
        scan = ScanPort(self.conn, self.cursor)
        scan.trigger = self.trigger
        back_off = " --host-timeout 120 --max-retries 5"
        scan.command = "nmap %s%s" % (device.ip, back_off)
        scan.device_id = device.id
        scan.insert_run_start()
        return scan

    def handle_ports(self, device: Device, ports: list):
        """Take ports found in scan to report and save."""
        if not ports:
            print('Device offline or no ports for %s' % device)
            return False

        num_ports = 0
        col_device_ports = DevicePorts(self.conn, self.cursor)
        device_ports = col_device_ports.get_by_device_id(device.id)
        for raw_port in ports:
            self.handle_port(device, device_ports, raw_port)
            num_ports += 1

        print('Device %s has %s ports open' % (device, num_ports))

    def handle_port(self, device, device_ports, raw_port):
        """Take a single port for device to report and save them."""
        this_dp = None
        for device_port in device_ports:
            if raw_port['number'] == device_port.port.port and \
                raw_port['protocol'] == device_port.port.protocol:
                this_dp = device_port
                this_dp.conn = self.conn
                this_dp.cursor = self.cursor
                this_port = device_port.port
                break

        if not this_dp:
            this_port = self.get_port(raw_port)
            this_dp = DevicePort(self.conn, self.cursor)
            this_dp.device_id = device.id
            this_dp.port_id = this_port.id
        this_dp.status = 'open'
        this_dp.last_seen = arrow.utcnow().datetime
        this_dp.save()

    def get_port(self, raw_port: dict) -> Port:
        """Get a port model from the port scan data.
           @todo: Load this data into memory to save db loads.
        """
        port = Port(self.conn, self.cursor)
        port.port = raw_port['number']
        port.protocol = raw_port['protocol']
        port.get_by_port_and_protocol()
        if not port.id:
            port.service = raw_port['service']
            port.save()
        return port

    def _complete_run_error(self, scan_log):
        scan_log.completed = True
        scan_log.success = False
        scan_log.message = 'Failed running command'
        scan_log.end_run()

# End File: lan_nanny/nanny-nanny/modules/models/scan_ports.py
