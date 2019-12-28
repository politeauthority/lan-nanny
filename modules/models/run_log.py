"""Run Log model

"""
import arrow


class RunLog():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.start_ts = None
        self.end_ts = None
        self.elapsed_time = None
        self.completed = None
        self.success = None

    def __repr__(self):
        return "<RunLog %s>" % self.id

    def get_by_id(self, run_id: int):
        """
        Gets a run from the `run_log` table based on it's run ID.

        """
        sql = """SELECT * FROM run_log WHERE id=%s""" % run_id
        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return {}
        
        self.build_from_list(run_raw)

        return self

    def get_last(self):
        """
        Gets the last run log form the `run_log` table.

        """
        sql = """SELECT * FROM run_log ORDER BY start_ts DESC LIMIT 1"""
        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return {}
        
        self.build_from_list(run_raw)

        return self

    def create(self):
        """
        Creates a new run log record.

        """
        now = arrow.utcnow().datetime

        sql = """
            INSERT INTO run_log
            (start_ts)
            VALUES ('%s')""" % now

        self.cursor.execute(sql)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self.cursor.lastrowid

    def update(self, run_log_id: int=None) -> bool:
        """
        Closes out a run log in the `run_log` table, setting the end time, elapsed time, and
        completed values.

        """
        run_id = None
        if run_log_id:
            run_id = run_log_id
        else:
            run_id = self.id

        current_run = self.get_by_id(run_id)
        self.end_ts = arrow.utcnow().datetime
        start = arrow.get(current_run.start_ts).datetime
        seconds = (self.end_ts - start).seconds
        self.elapsed_time = seconds

        sql = """
            UPDATE run_log
            SET
                end_ts = ?,
                elapsed_time = ?,
                completed = ?,
                success = ?
            WHERE id = ?"""
        the_update = (
            self.end_ts,
            self.elapsed_time,
            self.completed,
            self.success,
            run_id)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def build_from_list(self, raw: list):
        """
        Creates a run log from a raw row record.

        """
        self.id = raw[0]
        self.start_ts = raw[1]
        self.end_ts = raw[2]
        self.elapsed_time = raw[3]
        self.completed = raw[4]
        self.success = raw[5]


# End File: lan-nanny/modules/models/run_log.py
