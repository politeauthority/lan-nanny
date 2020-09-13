"""Scan Hosts Collection
Gets collections of scan host scan logs.

"""
from .base import Base
from ..models.scan_host import ScanHost


class ScanHosts(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanHosts, self).__init__(conn, cursor)
        self.table_name = ScanHost().table_name
        self.collect_model = ScanHost

    def get_avg_runtime(self, created_since_seconds: int=86400) -> float:
        """Get the average ScanHost scan run time over a period of time in seconds, defaults to 1
           day.
        """
        sql = """
            SELECT AVG(elapsed_time)
            FROM `%s`
            WHERE
                `created_ts` >= %s AND
                `completed` = true;
        """ % (self.table_name, created_since_seconds)
        self.cursor.execute(sql)
        raw_avg = self.cursor.fetchone()
        if not raw_avg:
            return None
        if raw_avg:
            avg = round(raw_avg[0], 2)
        else:
            avg = 0
        return avg


# End File: lan-nanny/lan_nanny/modules/collections/scan_hosts.py
