"""Scan Ports Collection
Gets collections of scan port scan logs.

"""

import arrow

from .base import Base
from ..models.scan_port import ScanPort


class ScanPorts(Base):

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor
        self.table_name = ScanPort().table_name
        self.collect_model = ScanPort

    def get_runs_24_hours(self) -> int:
        """Get number of scan_hosts runs over 24 hours"""
        now = arrow.utcnow()
        hour_24 = now.shift(hours=-24).datetime
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE end_ts >= '%s'""" % (self.table_name, hour_24)

    def get_row_length(self) -> int:
        """Get number of rows of scan_logs from the scan_log table."""
        sql = """
            SELECT count(*)
            FROM %s; """ % self.table_name
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        return raw[0]

# End File: lan-nanny/lan_nanny/modules/collections/scan_ports.py
