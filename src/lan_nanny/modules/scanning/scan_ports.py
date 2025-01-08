"""ScanPorts controls device port scanning efforts.

Device Port Scanning contains several steps

0 - Check if this should even run.
    - Is port scanning enabled?
    - Were there any results from the host scan which ran just before.
1 - Get devices that are port scan candidates
    Candidates must be:
        - Devices that were found in the prior host scan.
        *- Have .port_scan True.
        *- Has not been scanned since the options[scan-device-ports-interval] timeout.
2 - For each device eligible for a port scan
    - Start a new ScanPortLog
    - Run the port scan Nmap command
    - Parse the ports found into system Ports
    - Parse the ports found into DevicePorts


"""
from datetime import timedelta
import logging
import os
import subprocess
import time

import arrow

from . import parse_nmap
from ..models.device import Device
from ..models.device_port import DevicePort
from ..models.port import Port
from ..models.scan_port import ScanPort


class ScanPorts:

    def __init__(self, scan):
        self.args = scan.args
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.tmp_dir = scan.tmp_dir
        self.options = scan.options
        self.hosts = scan.hosts
        self.trigger = scan.trigger
        self.ports = {}

    def run(self):
        """ Main Runner for Scan Port."""
        logging.info("Running port scans")

        if self.args.force_port:
            logging.info('\tRunning Port Scan regardless of config because --force-port was used.')
        elif self.options['scan-ports-enabled'].value != True:
            logging.info('\tPort Scanning disabled')
            return False

        if not self.hosts:
            logging.info('\tNo hosts found in last scan, skipping port scan')
            return False

        port_scan_devices = self.get_port_scan_candidates()

        if not port_scan_devices:
            logging.info('\tNo devices ready for port scan, skipping.')
            return True

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
                logging.debug('\t%s does not have port scanning enabled' % host['device'])
                continue

            if not host['device'].last_port_scan:
                port_scan_devices.append(host['device'])
                continue
            # Remove devices that have been port scanned in x minutes.
            if host['device'].last_port_scan > host_port_scan_timeout:
                logging.debug('\t%s has been scanned in the last %s minutes' % (
                    host['device'],
                    host_port_scan_interval_mins))
                continue

            port_scan_devices.append(host['device'])

        limit = int(self.options['scan-ports-per-run'].value)
        if len(port_scan_devices) > limit:
            port_scan_devices = port_scan_devices[0:limit]
            logging.info("\tLimiting port scan to %s devices" % limit)

        return port_scan_devices

    def handle_device_port_scan(self, device: Device) -> bool:
        """Run device port scan and related processes for a single device."""
        device.conn = self.conn
        device.cursor = self.cursor

        # Lock the device from other scan processes.
        device.port_scan_lock = True
        device.save()

        # Start the device port scan log
        psl = self.create_device_port_scan_log(device)
        port_scan_results = self.scan_ports_cmd(psl, device)

        # Release device port scan lock.
        device.last_port_scan_id = psl.id
        device.last_port_scan = arrow.utcnow().datetime
        device.port_scan_lock = False
        device.save()

        # if port scanning failed for any reason.
        if not port_scan_results:
            logging.warning('\tPort scan failed for %s, will try again soon.' % device)
            # Check if this device has failed x port scans consecutively, if so update last_
            device.success = 0
            device.completed = 1
            device.save()
            return False

        self.handle_ports(device, port_scan_results, psl)

        device.save()
        return True

    def scan_ports_cmd(self, port_scan_log, device: Device) -> dict:
        """
        Run and manages an NMAP port scan for a single device to derive port data and returning
        those ports in a list of dicts.

        """
        start = time.time()
        port_scan_file = os.path.join(self.tmp_dir, "port_scan_%s.xml" % device.id)
        cmd = "%s -oX %s" % (port_scan_log.command, port_scan_file)
        logging.info('\tRunning port scan for %s' % device)
        # print('\t\t\tCmd: %s' % scan.command)

        try:
            subprocess.check_output(cmd, shell=True)
            port_scan_log.success = True
        except subprocess.CalledProcessError:
            print("CAUGHT EXCEPTION ON: %s" % cmd)
            end = time.time()
            self.scan.elapsed_time = end - start
            port_scan_log.success = False
            self._complete_run_error(self.scan, 'Error at NMAP command run')
            return False
        end = time.time()
        port_scan_log.elapsed_time = end - start
        port_scan_log.end_run()

        ports = parse_nmap.parse_xml(port_scan_file, 'ports')
        os.remove(port_scan_file)

        if ports == False:
            end = time.time()
            port_scan_log.elapsed_time = end - start
            self._complete_run_error(port_scan_log)
            return False

        return ports

    def create_device_port_scan_log(self, device: Device) -> bool:
        scan = ScanPort(self.conn, self.cursor)
        scan.trigger = self.trigger
        back_off = " --host-timeout 120 --max-retries 5"
        scan.command = "nmap %s%s" % (device.ip, back_off)
        scan.device_id = device.id
        scan.insert_run_start()
        return scan

    def handle_ports(self, device: Device, ports: list, psl) -> bool:
        """Take ports found in scan to report and save."""
        if not ports:
            print('\t\t\tDevice offline or no ports for %s' % device)
            return False

        num_ports = 0
        device.get_ports()
        for raw_port in ports:
            current_device_port = self.handle_port(raw_port, psl)
            self.handle_device_port(device, current_device_port, raw_port)
            num_ports += 1

        logging.info('\t\tDevice %s has %s ports open' % (device, num_ports))
        return True

    def handle_port(self, raw_port: dict, psl) -> Port:
        """Get a port model from the port scan data."""
        port_key = "%s/%s" % (raw_port['number'], raw_port['protocol'])
        if port_key in self.ports:
            this_port = self.ports[port_key]
        else:
            this_port = self.get_port(raw_port, psl)
            self.ports[port_key] = this_port
        return this_port

    def get_port(self, raw_port: dict, psl) -> Port:
        """Get a port model from the port scan data."""
        this_port = Port(self.conn, self.cursor)
        this_port.number = raw_port['number']
        this_port.protocol = raw_port['protocol']
        this_port.get_by_port_and_protocol()
        if not this_port.id:
            this_port.service = raw_port['service']
            this_port.first_port_scan_id = psl.id
        this_port.last_port_scan_id = psl.id
        this_port.updated_ts = arrow.utcnow().datetime
        this_port.save()
        return this_port

    def handle_device_port(self, device, port, port_scan_data):
        """
        Deals with the Device's relationship to a single Port.
        First it checks if the Device already has a relationship with the Port in question.
        If not creates one and sets the defaults.
        Once it has the DevicePort relationship it updates the DP object and is completed.

        """
        this_dp = None
        if device.ports:
            for device_port in device.ports:
                if device_port.port_id == port.id:
                    this_dp = device_port
                    break

        # If the Device hasn't had this port associated with it before, create a DevicePort obj
        if not this_dp:
            this_dp = DevicePort(self.conn, self.cursor)
            this_dp.device_id = device.id
            this_dp.port_id = port.id

        this_dp.last_seen = arrow.utcnow().datetime
        this_dp.updated_ts = arrow.utcnow().datetime
        this_dp.state = port_scan_data['state']
        this_dp.save()
        return this_dp

    def _complete_run_error(self, scan_log, msg: str=None) -> bool:
        logging.error('\t\tError running port scan for device, please try again soon.')
        if msg:
            logging.error("\tThe reported error was: %s" % msg)
        scan_log.completed = True
        scan_log.success = False
        scan_log.message = 'Failed running command'
        scan_log.end_run()
        return True

# End File: lan_nanny/nanny-nanny/modules/models/scan_ports.py
