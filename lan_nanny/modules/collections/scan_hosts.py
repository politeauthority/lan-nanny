"""Scan Hosts Collection
Gets collections of scan host scan logs.

"""

import arrow

from ..models.scan_host import ScanHost


class ScanHosts():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor
        self.table_name = ScanHost().table_name

    def get_all(self) -> list:
        """
        Get all run logs.

        """
        sql = """
            SELECT *
            FROM %s
            ORDER BY created_ts DESC
            LIMIT 20""" % self.table_name

        self.cursor.execute(sql)
        raw_scans = self.cursor.fetchall()
        scan_logs = []
        for raw_scan in raw_scans:
            scan = ScanHost(self.conn, self.cursor)
            scan.build_from_list(raw_scan)
            scan_logs.append(scan)
        return scan_logs

    def get_runs_24_hours(self):
        """
        Gets all devices in the database.

        """
        now = arrow.utcnow()
        hour_24 = now.shift(hours=-24).datetime
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE end_ts >= '%s'""" % (self.table_name, hour_24)

        self.cursor.execute(sql)
        raw_ret = self.cursor.fetchone()
        return raw_ret[0]

    def get_row_length(self) -> int:
        """Get number of rows of scan_logs from the scan_log table."""
        sql = """
            SELECT count(*)
            FROM %s; """ % self.table_name
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        return raw[0]


# End File: lan-nanny/modules/collections/scan_hosts.py
