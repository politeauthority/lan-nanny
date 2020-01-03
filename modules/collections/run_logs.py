"""Run Logs
Gets collections of run logs.

"""

import arrow

from ..models.run_log import RunLog


class RunLogs():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all(self) -> list:
        """
        Get all run logs.

        """
        sql = """
            SELECT *
            FROM run_logs
            ORDER BY created_ts DESC
            LIMIT 20"""

        self.cursor.execute(sql)
        raw_runs = self.cursor.fetchall()
        run_logs = []
        for raw_run in raw_runs:
            run = RunLog()
            run.build_from_list(raw_run)
            run_logs.append(run)
        return run_logs

    def get_runs_24_hours(self):
        """
        Gets all devices in the database.

        """
        now = arrow.utcnow()
        hour_24 = now.shift(hours=-24).datetime
        sql = """
            SELECT COUNT(*)
            FROM run_logs
            WHERE end_ts >= '%s'""" % hour_24

        self.cursor.execute(sql)
        raw_ret = self.cursor.fetchone()
        return raw_ret[0]

# End File: lan-nanny/modules/collections/run_logs.py
