"""Metrics

"""
from .collections.devices import Devices
from .collections.run_logs import RunLogs
from .models.run_log import RunLog


class Metrics:

    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def get_all_devices(self) -> list:
        """
        Gets all known devices.

        """
        devices = Devices(conn, cursor)
        all_devices = devices.get_all()
        return all_devices


    def get_favorite_devices(self) -> list:
        """
        Gets all favorite devices.

        """
        devices = Devices(conn, cursor)
        favorites = devices.get_favorites()
        return favorites


    def get_runs_24_hours(self) -> str:
        """

        """
        run_logs = RunLogs(conn, cursor)
        run_logs_24 = run_logs.get_runs_24_hours()
        return run_logs_24

    def get_last_run_log(self) -> RunLog:
        """
        Gets the last run log.

        """
        run_log = RunLog(conn, cursor)
        last_run_log = run_log.get_last()
        return last_run_log

# End File: lan-nanny/modules/metrics.py
