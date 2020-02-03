"""Device Witnesses
Gets collections of Device Witnesses.

"""
from datetime import timedelta

import arrow

from ..models.device_witness import DeviceWitness


class DeviceWitnesses:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor
        self.table_name = DeviceWitness().table_name

    def get_by_scan_id(self, scan_id: int) -> list:
        """Get all witness records from a scan_id."""
        sql = """
            SELECT *
            FROM %s
            WHERE scan_id = %s
            ORDER BY created_ts DESC;""" % (self.table_name, scan_id)

        self.cursor.execute(sql)
        raw_witnesses = self.cursor.fetchall()
        witnesses = []
        for raw_witness in raw_witnesses:
            witness = DeviceWitness(self.conn, self.cursor)
            witness.build_from_list(raw_witness, build_device=True)
            witnesses.append(witness)
        return witnesses

    def get_row_length(self) -> int:
        """Get number of rows of scan_logs from the scan_log table."""
        sql = """
            SELECT count(*)
            FROM %s; """ % self.table_name
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        return raw[0]

    def prune(self, days: int) -> bool:
        """Method to remove data older than x days from database."""
        days_back = arrow.utcnow().datetime - timedelta(days=days)
        sql = """
            DELETE FROM %s
            WHERE created_ts <= "%s"; """ % (self.table_name, days_back)
        self.cursor.execute(sql)
        self.conn.commit()

# End File: lan-nanny/modules/collections/device_witnesses.py
