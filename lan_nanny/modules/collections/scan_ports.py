"""Scan Ports Collection
Gets collections of scan port scan logs.

"""

import arrow

from .base import Base
from ..models.scan_port import ScanPort


class ScanPorts(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanPorts, self).__init__(conn, cursor)
        self.table_name = ScanPort().table_name
        self.collect_model = ScanPort

    def delete_device(self, device_id: int) -> bool:
        """Delete all device port records for a device_id."""
        sql = """DELETE FROM %s WHERE device_id=%s""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/collections/scan_ports.py
