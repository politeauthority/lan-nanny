"""Run Log - Model

"""
import arrow

from .base import Base


class RunLog(Base):

    def __init__(self, conn=None, cursor=None):
        super(RunLog, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'RunLog'
        self.table_name = 'run_logs'

        self.field_map = [
            {
                'name': 'end_ts',
                'type': 'datetime'
            },
            {
                'name': 'elapsed_time',
                'type': 'str'
            },
            {
                'name': 'completed',
                'type': 'bool'
            },
            {
                'name': 'success',
                'type': 'bool'
            },
            {
                'name': 'num_devices',
                'type': 'str'
            },
            {
                'name': 'scan_name',
                'type': 'str'
            }
        ]
        self.setup()

    def __repr__(self):
        return "<RunLog %s>" % self.id

    def get_last(self):
        """
        Gets the last run log form the `run_log` table.

        """
        sql = """SELECT * FROM %s ORDER BY created_ts DESC LIMIT 1""" % self.table_name
        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return {}

        self.build_from_list(run_raw)

        return self

    def insert_run_start(self):
        """
        Inserts a new record of the model.

        """
        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime

        insert_sql = "INSERT INTO %s (created_ts, completed) VALUES (?, ?)" % (self.table_name)
        self.cursor.execute(insert_sql, (self.created_ts, 0))
        self.conn.commit()
        self.id = self.cursor.lastrowid
        # @todo: make into logging NOT print
        print('New %s: %s' % (self.model_name, self))
        return True


# End File: lan-nanny/modules/models/run_log.py
