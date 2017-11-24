#!/usr/bin/env python
"""
lan_nanny.py

Usage:
    lan_nanny.py [options]
    lan_nanny.py (-h | --help)

Options:
    -h --help       Shows this screen.
    --ip=<ip>       The ip range to scan.
    --device        Add a name or person to a device.
    --report        Find the last time a device_id has been on network. (future)
    -d --debug      Straight tryina pull the bugs out.

"""

from docopt import docopt
import os
import sys
import xmltodict
from datetime import datetime
import requests

import conf
from modules.npappy import Npappy
from modules.models.device import Device
from modules.driver_mysql import DriverMysql

db = DriverMysql(conf.mysql_connection)


class LanNanny(object):

    def run(self, rgs):
        """
        Main runner

        :param args: Docopt CLI args
        :type args: dict
        """
        if os.geteuid() != 0:
            exit("""You need to have root privileges to run this script.\n
            Please try again, this time using 'sudo'. Exiting.""")
        if len(sys.argv) > 1:
            scans = args['--ip']
        # else:
        #     scans = prep_dynamic_scan()
        if ',' in scans:
            scans = args['--ip']
        else:
            scans = [scans]
        print 'Running scan, this may take awhile depending on the size of the ip range.'
        network_devices = {}
        for scan in scans:
            scan_file = Npappy().hosts(scan)
            network_devices = dict(network_devices, **self.parse_nmap(scan_file))
        print 'Proccessing scan output'
        self.store_data(network_devices)

    def save_new_device(self, device):
        """
        Inserts a row into the devices table.

        :return: The new id of the device. (device_id)
        :rtype: int
        """
        vals = {
            # 'name': device['name'],
            'mac': device['mac'],
            'last_seen': device['scan_time'],
            'last_ip': device['current_ip'],
            'last_hostname': '',
        }

        Device().save(vals, db)

    def save_wittness(self, device_id, time_seen):
        """
        Saves a record into the witness table, logging the event of seeing a particular unit.

        :param device_id: The witnessed devices
        :param device_id: int
        :param time_seen: The time the device was seen
        :param time_seen: Datetime obj
        """
        qry = """
            INSERT INTO `lan_nanny`.`witness`
            (`device_id`, `date`, `seen_by`)
            VALUES(%s, "%s", "%s"); """ % (device_id, time_seen, conf.machine_id)
        db.ex(qry)

    def parse_scan_time(self, string_):
        return datetime.strptime(string_, '%a %b  %d %H:%M:%S %Y')

    def parse_nmap(self, xml_phile):
        """
        Reads and parses a Nmap output files.

        :param xml_phile: Path to the Nmap output XML file.
        :type xml_phile: str
        """
        print '  Parsing %s' % xml_phile
        scan_string = open(xml_phile)
        netscan = dict(xmltodict.parse(scan_string))
        network_devices = {}
        scan_time = self.parse_scan_time(netscan['nmaprun']['runstats']['finished']['@timestr'])
        for host in netscan['nmaprun']['host']:
            if host['status']['@state'] == 'up':
                try:
                    ip = host['address'][0]['@addr']
                    mac = host['address'][1]['@addr']
                except KeyError:
                    continue
                network_devices[mac] = {
                    'name': '',
                    'mac': mac,
                    'current_ip': ip,
                    'scan_time': scan_time
                }
        return network_devices

    def store_data(self, network_devices):
        """
        """
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(network_devices)
        known_devices = Device().get_all(db)
        print 'Found %s Devices of %s known\n' % (len(network_devices), len(known_devices))
        for mac, info in network_devices.iteritems():
            scanned_device_id = False
            for d_id, device in known_devices.iteritems():
                if device['mac'] == mac:
                    scanned_device_id = d_id
            if not scanned_device_id:
                scanned_device_id = Device().save(info, db)
                print 'Found new device %s at ip: %s' % (mac, info['current_ip'])
            else:
                Device().update(info, db)

            if scanned_device_id in known_devices:
                if known_devices[scanned_device_id]['name']:
                    print 'We found Device: %s' % known_devices[scanned_device_id]['name']
                else:
                    Device().mac_lookup(mac, db)
                    print 'Unknown: %s %s' % (info['mac'], info['current_ip'])
                # print known_devices[scanned_device_id]
            self.save_wittness(scanned_device_id, info['scan_time'])


if __name__ == '__main__':
    args = docopt(__doc__)
    print args

    LanNanny().run(args)

# End File: politeauthority/tools/netscan.py
