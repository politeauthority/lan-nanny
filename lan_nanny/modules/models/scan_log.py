"""Scan Log - Model

"""
import arrow

from .base import Base


class ScanLog(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanLog, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'scan_logs'

        self.field_map = [
            {
                'name': 'end_ts',
                'type': 'datetime'
            },
            {
                'name': 'elapsed_time',
                'type': 'int'
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
                'name': 'units',
                'type': 'int',
                'default': 0,
            },
            {
                'name': 'scan_type',
                'type': 'str'
            },
            {
                'name': 'command',
                'type': 'str'
            },
            {
                'name': 'trigger',
                'type': 'str'
            },
        ]
        self.setup()

    def __repr__(self):
        return "<ScanLog %s>" % self.id

    def get_last(self, scan_type):
        """
        Gets the last run log form the `scan_log` table.

        """
        sql = """
            SELECT *
            FROM %s
            WHERE
                scan_type="%s"
            ORDER BY created_ts DESC
            LIMIT 1""" % (self.table_name, scan_type)
        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return False

        self.build_from_list(run_raw)

        return self

    def insert_run_start(self, scan_type: str):
        """
        Inserts a new record of the model.

        """
        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime
        self.setup()
        insert_sql = """
            INSERT INTO %s
            (created_ts, completed, scan_type, trigger)
            VALUES (?, ?, ?, ?)""" % (self.table_name)

        self.cursor.execute(insert_sql, (self.created_ts, 0, scan_type, self.trigger))
        self.conn.commit()
        self.id = self.cursor.lastrowid
        self.scan_type = scan_type
        return True

    def end_run(self):
        self.end_ts = arrow.utcnow()
        self.elapsed_time = (arrow.utcnow() - self.created_ts).seconds
        self.completed = True
        self.save()

# End File: lan-nanny/lan_nanny/modules/models/scan_log.py
