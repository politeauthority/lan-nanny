"""Alert Event

"""
from .base import Base


class AlertEvent(Base):

    def __init__(self, conn=None, cursor=None):
        super(AlertEvent, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'AlertEvent'
        self.table_name = 'alert_events'
        self.field_map = [
            {
                'name': 'alert_id',
                'type': 'int',
            },
            {
                'name': 'event_type',
                'type': 'str'
            }
        ]
        self.setup()

    def check_active(self, device_id: int, alert_type: str) -> bool:
        """
        Checks the `alerts` table for active alerts for a device and alert type.

        """
        sql = """
            SELECT *
            FROM alerts
            WHERE
                active=1 AND
                device_id=? AND
                alert_type=?
            ORDER BY created_ts DESC
            LIMIT 1 """
        self.cursor.execute(sql, (device_id, alert_type))
        alert_raw = self.cursor.fetchone()
        if alert_raw:
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

# End File: lan-nanny/modules/models/alert_event.py
