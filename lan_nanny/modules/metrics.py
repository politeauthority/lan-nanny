"""Metrics

"""
from .collections.devices import Devices
from .collections.scan_logs import ScanLogs
from .models.scan_log import ScanLog


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

    def get_runs_24_hours(self):
        """

        """
        scan_logs = ScanLogs(self.conn, self.cursor)
        scan_logs_24 = scan_logs.get_runs_24_hours()
        return scan_logs_24

    def get_last_host_scan(self) -> ScanLog:

        """
        Gets the last run log.

        """
        scan_log = ScanLog(self.conn, self.cursor)
        scan_log.get_last('host')
        return scan_log


    def get_dashboard_online_chart(self, devices):
        """Create the differential of online devices vs total devices."""
        total = len(devices)
        the_num = 0
        for device in devices:
            if device.online():
                the_num += 1
        return [the_num, total - the_num]

# End File: lan-nanny/lan_nanny/modules/metrics.py
