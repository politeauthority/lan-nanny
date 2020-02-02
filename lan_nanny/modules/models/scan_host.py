"""Scan Host - Model

"""
import arrow

from .base import Base


class ScanHost(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanHost, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'scan_hosts'

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
                'name': 'command',
                'type': 'str'
            },
            {
                'name': 'trigger',
                'type': 'str'
            },
        ]
        self.setup()

    def get_last(self):
        """Get the last run log form the `scan_hosts` table."""
        sql = """
            SELECT *
            FROM %s
            ORDER BY created_ts DESC
            LIMIT 1""" % (self.table_name)

        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return False

        self.build_from_list(run_raw)

        return self

    def insert_run_start(self) -> bool:
        """Insert a new record of the model."""
        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime
        self.setup()
        insert_sql = """
            INSERT INTO %s
            (created_ts, completed, trigger)
            VALUES (?, ?, ?)""" % (self.table_name)

        self.cursor.execute(insert_sql, (self.created_ts, 0, self.trigger))
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return True

    def end_run(self):
        """End a scan run."""
        self.end_ts = arrow.utcnow()
        self.elapsed_time = (arrow.utcnow() - self.created_ts).seconds
        self.completed = True
        self.save()

# End File: lan-nanny/lan_nanny/modules/models/scan_host.py
