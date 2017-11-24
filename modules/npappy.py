#!/usr/bin/env python
"""Npappy
Reads, parses and provides Nmap data

"""

import os
import subprocess
from datetime import datetime
import xmltodict
from politeauthority import environmental
from politeauthority import common


class Npappy(object):

    def hosts(self, ip_range):
        self.output_file = os.path.join(
            self.__save_dir(),
            'nmap_%s.xml' % str(datetime.now()).replace(' ', '-')
        )
        cmd = 'nmap -sP -oX %s %s' % (
            self.output_file,
            ip_range)
        subprocess.check_output(
            cmd,
            shell=True)
        return self.output_file

    def __save_dir(self):
        the_dir = os.path.join(
            environmental.get_temp_dir(),
            'netscan'
        )
        if not os.path.exists(the_dir):
            os.makedirs(the_dir)
        return the_dir

    def parse_nmap(self, xml_phile):
        """
            Parses a nmap file into a dict
            @params
                xml_phile: nmap xml file location
        """
        scan_string = open(xml_phile)
        netscan = dict(xmltodict.parse(scan_string))
        network_devices = {}
        scan_time = self.__parse_nmap_scan_time(netscan['nmaprun']['runstats']['finished']['@timestr'])
        if 'host' not in netscan['nmaprun']:
            return network_devices
        for host in netscan['nmaprun']['host']:
            if host['status']['@state'] == 'up':
                if 'address' in host and len(host['address']) > 1:
                    print host['address'][0]
                    ip = host['address'][0]['@addr']
                    mac = host['address'][1]['@addr']
                    network_devices[mac] = {
                        'name': '',
                        'mac': mac,
                        'current_ip': ip,
                        'scan_time': scan_time
                    }
        return network_devices

    def __parse_nmap_scan_time(self, string_):
        return datetime.strptime(string_, '%a %b  %d %H:%M:%S %Y')

    def run_iwlist(self, interface):
        output_file = self.cmd_iwlist(interface)
        parsed_iwlist = self.parse_iwlist(output_file)
        return parsed_iwlist

    def cmd_iwlist(self, interface):
        output_file = os.path.join(
            self.__save_dir(),
            'iwlist_%s.txt' % str(datetime.now()).replace(' ', '-')
        )
        cmd = 'sudo iwlist %s scan > %s' % (interface, output_file)
        subprocess.check_output(
            cmd,
            shell=True)
        return output_file

    def parse_iwlist(self, phile_location):
        fo = open(phile_location, "r+")
        content = fo.read()
        cells = content.split('Cell ')
        del cells[0]
        nodes = {}
        for cell in cells:
            for l in cell.split('\n'):
                if '- Address: ' in l:
                    ap_mac = l[l.find('Address: ')+9:].strip()
                    nodes[ap_mac] = {}
                elif 'ESSID:' in l:
                    nodes[ap_mac]['ESSID'] = l.split('ESSID:"')[1].replace('"', "").strip()
                elif 'Channel:' in l:
                    nodes[ap_mac]['channel'] = self.__clean_values_at(l, 'Channel:')
                elif 'Frequency:' in l:
                    tmp = self.__clean_values_at(l, 'Frequency:')
                    tmp = tmp[:tmp.find('(')]
                    nodes[ap_mac]['frequency'] = tmp
                elif 'Encryption key:' in l:
                    tmp = l.split('Encryption key:')[1].replace('"', "").strip()
                    if tmp == 'off':
                        nodes[ap_mac]['encryption_key'] = False
                    else:
                        nodes[ap_mac]['encryption_key'] = True
                elif 'WPA Version' in l:
                    nodes[ap_mac]['encryption_type'] = l[l.find('WPA Version'):].strip()
                elif 'Quality=' in l:
                    tmp = self.__clean_values_at(l, 'Quality=')
                    low = int(tmp[0:tmp.find('/')])
                    high = int(tmp[tmp.find('/')+1:tmp.find('Signal')].strip())
                    signal_strength = common.get_percentage(low, high)
                    nodes[ap_mac]['signal_strength'] = signal_strength
                    signal_level = self.__clean_values_at(l, 'Signal level=')
                    signal_level = int(signal_level[:signal_level.find('dBm')])
                    nodes[ap_mac]['signal_level'] = signal_level
        return nodes

    def __clean_values_at(self, source, where_at):
        return source[source.find(where_at) + len(where_at):].replace('"', '').strip()

# EndFile: politeauthority/netscan.py
