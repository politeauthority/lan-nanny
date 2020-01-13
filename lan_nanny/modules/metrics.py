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

    def get_last_run_log(self, scan_type) -> ScanLog:
        """
        Gets the last run log.

        """
        scan_log = ScanLog(self.conn, self.cursor)
        last_scan_log = scan_log.get_last(scan_type)
        return last_scan_log

# End File: lan-nanny/lan_nanny/modules/metrics.py
