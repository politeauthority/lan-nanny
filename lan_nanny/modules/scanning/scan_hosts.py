"""Scan Hosts - Runs host NMAP scans and saves the results.

"""
from datetime import datetime
import logging
import os
import subprocess
import time

import arrow

from . import parse_nmap
from . import parse_arp
from ..models.scan_host import ScanHost
from ..models.device import Device
from ..models.device_mac import DeviceMac
from ..models.device_witness import DeviceWitness


class ScanHosts:

    def __init__(self, scan):
        self.args = scan.args
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.tmp_dir = scan.tmp_dir
        self.scan_file = os.path.join(self.tmp_dir, 'host-scan.xml')
        self.trigger = scan.trigger
        self.run_success = True
        self.hosts = []
        self.new_devices = []

    def run(self) -> list:
        """Run host nmap scan."""
        self.setup()
        logging.info('Running Host Scan')

        if self.args.force_host:
            logging.info('\tRunning Host Scan regardless of config because --force-host was used.')
        elif self.options['scan-hosts-enabled'].value != True:
            logging.info('\tHost scanning disabled. Go to settings to renable.')
            self._abort_run('Scanning disabled by option.')
            return False

        if self.options['scan-hosts-tool'].value == 'arp':
            self.scan_with_arp()
        else:
            self.scan_with_nmap()
        
        # self.scan_with_nmap()

        self._complete_run()
        self.handle_devices()
        return (self.hosts, self.new_devices, self.scan_log)

    def setup(self):
        """Set up the scan hosts run."""
        self.scan_log = ScanHost(self.conn, self.cursor)
        self.scan_log.trigger = self.trigger

    def scan_with_nmap(self) -> bool:
        """Run the port scan operation."""
        logging.info('Scanning with Nmap')
        scan_range = self.options['scan-hosts-range'].value
        start_ts = time.time()

        logging.info('\tScan Range: %s' % scan_range)
        self.scan_log.command = "nmap -sP %s" % scan_range
        cmd = "nmap -sP %s -oX %s" % (scan_range, self.scan_file)
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            logging.error('Error running scan, please try again')
            end_ts = time.time()
            self._complete_run_error(start_ts, end_ts, 'Running Scan.')
            self.run_success = False

        end_ts = time.time()
        hosts = parse_nmap.parse_xml(self.scan_file, 'hosts')
        if not hosts:
            self._complete_run_error('Reading XML')
            self.run_success = False

        if self.run_success:
            self.scan_log.elapsed_time = round(end_ts - start_ts, 2)
        
        self.hosts = hosts
        self.scan_log.save()

        return True

    def scan_with_arp(self) -> bool:
        """Run the port scan operation."""
        scan_range = self.options['scan-hosts-range'].value
        start_ts = time.time()
        scan_range = "192.168.50.0/23"

        logging.info('Scanning with Arp')
        logging.info('\tScan Range: %s' % scan_range)
        self.scan_log.command = "/usr/sbin/arp-scan %s" % scan_range
        self.scan_log.created_ts = arrow.utcnow().datetime
        self.scan_log.save()
        arp_response = subprocess.check_output(self.scan_log.command, shell=True)
        # try:
        #     arp_response = subprocess.check_output(self.scan_log.command, shell=True)
        # except subprocess.CalledProcessError:
        #     logging.error('Error running scan, please try again')
        #     end_ts = time.time()
        #     self._complete_run_error(start_ts, end_ts, 'Running Scan.')
        #     self.run_success = False
        end_ts = time.time()

        hosts = parse_arp.parse_hosts(arp_response)
        if not hosts:
            self._complete_run_error('Reading XML')
            self.run_success = False

        if self.run_success:
            self.scan_log.elapsed_time = round(end_ts - start_ts, 2)
        
        self.hosts = hosts
        self.scan_log.save()

        return True

    def handle_devices(self):
        """Handles devices found in NMap scan, creating records for new devices, updating last seen
           for already known devices and saving witness for all found devices.
        """
        if not self.hosts:
            logging.warning('\tNo hosts found or error encountered.')
            return False
        logging.info('\tFound %s devices:' % len(self.hosts))
        self.new_devices = []

        scan_time = arrow.utcnow().datetime
        count = 0
        for host in self.hosts:
            if not host['mac']:
                logging.debug('\tCouldnt find mac for device, skipping')
                continue

            device = Device(self.conn, self.cursor)
            device.get_by_mac(host['mac'])
            new = False
            # Create a new device
            if not device.id:
                new = True
                device.first_seen = scan_time
                device.name = host['vendor']
                device.vendor = host['vendor']

                device.mac = host['mac']
                if self.options['scan-ports-default'].value:
                    device.port_scan = True

            device.name = self._set_device_name(device, host)
            device.last_seen = scan_time
            device.ip = host['ip']

            device.save()
            self.hosts[count]['device'] = device
            count += 1

            new_device_str = ""
            if new:
                self.new_devices.append(device)
                new_device_str = "\t- New Device"
            logging.debug('\t\t%s - %s%s' % (device.name, device.ip, new_device_str))

            self.save_witness(device, scan_time)

        self.hosts = self.prune_hosts_wo_mac()

    def prune_hosts_wo_mac(self) -> list:
        """The device running the scan is not able to find its own mac, we need to filter that out,
           and potentially any other device without a mac, though I think only localhost will have 
           this issue.

        """
        pruned_hosts = []
        for host in self.hosts:
            if not host['mac']:
                continue
            pruned_hosts.append(host)
        return pruned_hosts

    def _set_device_name(self, device: Device, host: dict):
        """Set the device name to the host name if available, then the vendor if nothing else is
           available it sets the device name to the mac address.

        """
        # if we don't have a device name and we have a hostname, use the hostname
        if not device.name and 'hostname' in host and host['hostname']:
            return host['hostname']

        # if the device name is the same as vendor, and we have a hostname, use the hostname
        if device.name == device.vendor and 'hostname' in host and host['hostname']:
            return host['hostname']

        # at this point if we have a device name, lets use that.
        if device.name:
            return device.name

        # if no device name, but vendor, use the vendor
        if device.vendor:
            return device.vendor

        # if nothing else, use the mac as the device name
        return device.mac

    def save_witness(self, device: Device, scan_time: datetime) -> bool:
        """Create a record in the `device_witness` table of the devices id and scan time."""
        witness = DeviceWitness(self.conn, self.cursor)
        witness.device_id = device.id
        witness.scan_id = self.scan_log.id
        witness.insert()
        return True

    def _complete_run(self):
        """Closes out the ScanHost run log entry as success."""
        self.scan_log.completed = 1
        self.scan_log.success = 1
        self.scan_log.end_ts = arrow.utcnow().datetime
        if self.hosts:
            self.scan_log.units = len(self.hosts)
        else:
            self.scan_log.units = 0
        self.scan_log.scan_range = self.options['scan-hosts-range'].value
        self.scan_log.save()
        return True

    def _complete_run_error(self, error_section: str):
        """Closes out the ScanHost log entry as a fail."""
        self.scan_log.completed = True
        self.scan_log.success = False
        self.scan_log.message = error_section
        self.scan_log.save()
        return True

    def _abort_run(self, error_section: str):
        """Closes out scan host run log entry as an abort."""
        self.scan_log.completed = False
        self.scan_log.success = False
        self.scan_log.message = error_section
        self.scan_log.save()
        return True


# End File: lan-nanny/lan_nanny/modules/scanning/scan_hosts.py
