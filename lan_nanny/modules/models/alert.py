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
        self.device = None
        self.events = []

    def __repr__(self):
        if self.id:
            return "<Alert %s>" % self.id
        return "<Alert>"

    def get_active(self, device_id: int, alert_type: str) -> bool:
        """
        Checks the `alerts` table for active alerts for a device and alert type.

        """
        sql = """
            SELECT *
            FROM alerts
            WHERE
                active = 1 AND
                device_id = ? AND
                alert_type = ?
            ORDER BY created_ts DESC
            LIMIT 1 """
        self.cursor.execute(sql, (device_id, alert_type))
        alert_raw = self.cursor.fetchone()
        if alert_raw:
            self.build_from_list(alert_raw, build_device=False)
            return True
        return False

    def get_by_id(self, model_id: int, build_device: bool=False, build_alert_events: bool=False):
        """
        Gets an alert from the `alerts` table based on it's alert ID.

        """
        sql = """SELECT * FROM %s WHERE id=%s""" % (self.table_name, model_id)
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        if not raw:
            return False

        self.build_from_list(raw, build_device=build_device, build_alert_events=build_alert_events)

        return self

    def delete_device(self, device_id: int) -> bool:
        """
        Deletes all records from the `alerts` table containing a device_id, this should be
        performed when deleting a device.

        """
        sql = """DELETE FROM alerts WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

    def delete_alert_events(self) -> bool:
        """
        Deletes all alert_event records for an alert.

        """
        sql = """DELETE FROM alert_events WHERE alert_id = %s """ % self.id
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/models/alert.py
