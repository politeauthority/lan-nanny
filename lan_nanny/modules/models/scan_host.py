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
                'type': 'float'
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
            {
                'name': 'message',
                'type': 'str'
            },
        ]
        self.setup()

    def insert_run_start(self) -> bool:
        """Insert a new record of the model."""
        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime
        self.setup()
        insert_sql = """
            INSERT INTO %s
            (`created_ts`, `trigger`)
            VALUES (?, ?)""" % self.table_name
        insert_sql = insert_sql.replace("?", "%s")
        self.cursor.execute(insert_sql, (self.created_ts, self.trigger))
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return True

    def end_run(self):
        """End a scan run."""
        self.end_ts = arrow.utcnow().datetime
        self.completed = True
        self.save()

# End File: lan-nanny/lan_nanny/modules/models/scan_host.py
