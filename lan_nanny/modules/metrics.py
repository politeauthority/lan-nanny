"""Metrics

"""
import json

from .collections.devices import Devices
from .collections.scan_hosts import ScanHosts
from .models.scan_host import ScanHost



class Metrics:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all_devices(self) -> list:
        """
        Gets all known devices.

        """
        devices = Devices(self.conn, self.cursor)
        all_devices = devices.get_all()
        return all_devices

    def get_favorite_devices(self) -> list:
        """
        Gets all favorite devices.

        """
        devices = Devices(self.conn, self.cursor)
        favorites = devices.get_favorites()
        return favorites

    def get_scan_host_runs_24_hours(self):
        """Gets numeric number of host scans over 24 hours. """
        scan_hosts = ScanHosts(self.conn, self.cursor)
        scan_hosts_24 = scan_hosts.get_runs_24_hours()
        return scan_hosts_24

    def get_last_host_scan(self) -> ScanHost:
        """Get the last host scan run."""
        scan_host = ScanHost(self.conn, self.cursor)
        scan_host.get_last()
        return scan_host

    def get_dashboard_online_chart(self, devices):
        """Create the differential of online devices vs total devices."""
        total = len(devices)
        the_num = 0
        for device in devices:
            if device.online():
                the_num += 1
        return [the_num, total - the_num]

    def get_device_vendor_grouping(self) -> dict:
        sql = """
            SELECT DISTINCT vendor, count(*)
            FROM devices
            GROUP BY 1
            ORDER BY 1 ASC 
            ;"""
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        ret = {
            'vendors': [],
            'vendors_js': [],
            'values': [],
            'values_js': [],

        }
        for row in raw:
            vendor_name = row[0]
            if not vendor_name:
                vendor_name = 'Unknown'
            ret['vendors'].append(vendor_name)
            ret['vendors_js'].append(vendor_name)
            
            value = row[1]
            ret['values'].append(value)
            ret['values_js'].append(value)

        ret['vendors_js'] = json.dumps(ret['vendors_js'])
        ret['values_js'] = json.dumps(ret['values_js'])

        return ret

# End File: lan-nanny/lan_nanny/modules/metrics.py
