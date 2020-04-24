"""Metrics

"""
import json

from .collections.devices import Devices
from .collections.device_witnesses import DeviceWitnesses
from .collections.scan_hosts import ScanHosts
from .collections.scan_ports import ScanPorts
from .models.scan_host import ScanHost
from . import utils


class Metrics:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all_scans_24(self) -> int:
        seconds_in_24_hours = 60 * 60 * 24
        col_scan_host = ScanHosts(self.conn, self.cursor)
        col_scan_ports = ScanPorts(self.conn, self.cursor)

        total = col_scan_host.get_count_since(seconds_in_24_hours) + \
            col_scan_ports.get_count_since(seconds_in_24_hours)
        return total

    def get_favorite_devices(self) -> list:
        """Get all favorite devices."""
        devices = Devices(self.conn, self.cursor)
        favorites = devices.get_favorites()
        return favorites

    def get_dashboard_online_chart(self, devices):
        """Create the differential of online devices vs total devices."""
        total = len(devices)
        the_num = 0
        for device in devices:
            if device.online():
                the_num += 1
        return [the_num, total - the_num]

    def get_device_vendor_grouping(self) -> dict:
        """Get devices grouped by vendors."""
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

    def get_device_presence_over_time(self, device, hours: int=24) -> dict:
        """Get a single device's presence on network over a period of time as a percentage value
        based on DeviceWitness count and Host Scans over that period of time.
        """
        wd = DeviceWitnesses(self.conn, self.cursor)
        sh = ScanHosts(self.conn, self.cursor)
        seconds_in_24_hours = 60 * 60 * hours
        # wd.get_count_since(seconds_in_24_hours)
        device_witness = wd.get_count_since_by_device_id(device.id, seconds_in_24_hours)
        host_scans = sh.get_count_since(seconds_in_24_hours)
        ret = {
            'device_witness': device_witness,
            'host_scans': host_scans,
            'device_online_percent': utils.get_percent(host_scans, device_witness)
        }

        return ret

# End File: lan-nanny/lan_nanny/modules/metrics.py
