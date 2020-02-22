"""Alert - Model

"""
from .base import Base
from .device import Device


class Alert(Base):

    def __init__(self, conn=None, cursor=None):
        super(Alert, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'alerts'
        self.field_map = [
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
            {
                'name': 'last_observed_ts',
                'type': 'datetime'
            },
            {
                'name': 'resolved_ts',
                'type': 'datetime'
            },
            {
                'name': 'kind',
                'type': 'str'
            },
            {
                'name': 'notification_sent',
                'type': 'int'
            },
            {
                'name': 'acked',
                'type': 'int'
            },
            {
                'name': 'acked_ts',
                'type': 'datetime'
            },
            {
                'name': 'active',
                'type': 'bool'
            },
            {
                'name': 'message',
                'type': 'str'
            },

        ]
        self.setup()

    def __repr__(self):
        if self.kind:
            return "<Alert %s>" % self.kind
        return "<Alert>"

    def get_active(self, alert_type: str) -> bool:
        """
        Checks the `alerts` table for active alerts for a device and alert type.

        """
        sql = """
            SELECT *
            FROM alerts
            WHERE
                active = 1 AND
                alert_type = ?
            ORDER BY created_ts DESC
            LIMIT 1 """
        self.cursor.execute(sql, (alert_type))
        alert_raw = self.cursor.fetchone()
        if alert_raw:
            self.build_from_list(alert_raw)
            return True
        return False

    def delete_device(self, device_id: int) -> bool:
        """
        Deletes all records from the `alerts` table containing a device_id, this should be
        performed when deleting a device.

        """
        sql = """DELETE FROM alerts WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/models/alert.py
