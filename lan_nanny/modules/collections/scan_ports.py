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

# End File: lan-nanny/lan_nanny/modules/collections/scan_ports.py
