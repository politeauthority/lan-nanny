"""Scan Port - Model

"""
import arrow

from .base import Base


class ScanPort(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanPort, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'scan_ports'

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
                'name': 'device_id',
                'type': 'int'
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

    def insert_run_start(self):
        """Insert a new record of the model."""
        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime
        self.setup()
        insert_sql = """
            INSERT INTO %s
            (created_ts, device_id, completed, trigger, command)
            VALUES (?, ?, ?, ?, ?)""" % (self.table_name)

        values = (
            self.created_ts,
            self.device_id,
            0,
            self.trigger,
            self.command)

        self.cursor.execute(insert_sql, values)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return True

    def end_run(self):
        """End a scan run."""
        self.end_ts = arrow.utcnow().datetime
        self.elapsed_time = (arrow.utcnow() - self.created_ts).seconds
        self.completed = True
        self.save()

# End File: lan-nanny/lan_nanny/modules/models/scan_port.py
