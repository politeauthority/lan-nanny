"""Alert

"""
import arrow

from .base import Base
from .device import Device


class Alert(Base):

    def __init__(self, conn=None, cursor=None):
        super(Alert, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'Alert'
        self.table_name = 'alerts'
        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int',
            },
            {
                'name': 'alert_type',
                'type': 'str'
            },
            {
                'name': 'time_delta',
                'type': 'int'
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
                'type': 'int'
            },

        ]
        self.set_defaults()
        self.device = None

    def __repr__(self):
        if self.id:
            return "<Alert %s>" % self.id
        return "<Alert>"


    def check_active(self, device_id: int, alert_type: str) -> bool:
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



    def get_by_id(self, model_id: int, build_device=None):
        """
        Gets an alert from the `alerts` table based on it's alert ID.

        """
        sql = """SELECT * FROM %s WHERE id=%s""" % (self.table_name, model_id)
        print(sql)
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        if not raw:
            return False

        self.build_from_list(raw)

        return self


    def build_from_list(self, raw: list, build_device: bool=True):
        """
        """
        c = 0
        for field in self.total_map:
            setattr(self, field['name'], raw[c])
            c += 1
        if build_device:
            self.device = Device(self.conn, self.cursor)
            self.device.get_by_id(self.device_id)

        return True

# End File: lan-nanny/modules/models/alert.py
