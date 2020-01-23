"""ScanPrune
Procedural tool that runs at the end of a scan to prune data older than the setting `db-prune-days`
describes.

"""
from ..collections.witnesses import Witnesses


class ScanPrune:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options

    def run(self):
        """
        Main Runner for Scan Port.

        """
        if self.options['db-prune-days'].value:
            days = int(self.options['db-prune-days'].value)
        else:
            return
        print('Running prune of data older than %s days' % days)
        Witnesses(self.conn, self.cursor).prune(days)


# End File: lan_nanny/nanny-nanny/modules/scanning/scan_prune.py
