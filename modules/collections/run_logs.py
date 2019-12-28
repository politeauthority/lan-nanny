"""Devices
Gets collections of devices.

"""
from datetime import datetime

import arrow

from ..models.device import Device


class RunLogs():

    def __init__(self):
        self.conn = None
        self.cursor = None

    def get_runs_24_hours(self):
        """
        Gets all devices in the database.

        """
        now = arrow.utcnow()
        hour_24 = now.shift(hours=-24).datetime
        sql = """
            SELECT COUNT(*)
            FROM run_log
            WHERE end_ts >= '%s'""" % hour_24

        self.cursor.execute(sql)
        raw_ret = self.cursor.fetchone()
        return raw_ret[0]

# End File: lan-nanny/modules/collections/run_logs.py
