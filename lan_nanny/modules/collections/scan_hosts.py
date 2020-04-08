"""Scan Hosts Collection
Gets collections of scan host scan logs.

"""

import arrow

from .base import Base
from ..models.scan_host import ScanHost


class ScanHosts(Base):

    def __init__(self, conn=None, cursor=None):
        """ Store Sqlite conn and model table_name as well as the model obj for the collections
            target model.
        """
        super(ScanHosts, self).__init__(conn, cursor)
        self.table_name = ScanHost().table_name
        self.collect_model = ScanHost

# End File: lan-nanny/lan_nanny/modules/collections/scan_hosts.py
