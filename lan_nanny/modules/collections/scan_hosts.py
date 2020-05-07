"""Scan Hosts Collection
Gets collections of scan host scan logs.

"""
from datetime import timedelta

import arrow

from .base import Base
from ..models.scan_host import ScanHost


class ScanHosts(Base):

    def __init__(self, conn=None, cursor=None):
        """Create the ScanHosts Collection with the ScanHost table name and model base."""
        super(ScanHosts, self).__init__(conn, cursor)
        self.table_name = ScanHost().table_name
        self.collect_model = ScanHost


# End File: lan-nanny/lan_nanny/modules/collections/scan_hosts.py
