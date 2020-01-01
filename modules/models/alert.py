"""Alert

"""
import arrow

from .device import Device


class Alert():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.created_ts = None
        self.device_id = None
        self.alert_type = None
        self.time_delta = None
        self.notification_sent = None
        self.acked = None
        self.acked_ts = None
        self.active = None
        self.device = None

    def __repr__(self):
        if self.id:
            return "<Alert %s>" % self.id
        return "<Alert>"

    def get_by_id(self, alert_id: int, build_device: bool=None):
        """
        Gets an alert from the `alerts` table based on it's alert ID.

        """
        sql = """SELECT * FROM alerts WHERE id=%s""" % alert_id
        self.cursor.execute(sql)
        alert_raw = self.cursor.fetchone()
        if not alert_raw:
            return {}

        self.build_from_list(alert_raw, build_device)

        return self

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

    def create(self, raw_alert: dict={}):
        """
        Creates an alert by inserting into the `alerts` table, returning the alert object.

        """
        self.build_from_dict(raw_alert)

        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime

        sql = """
            INSERT INTO alerts
            (created_ts, device_id, alert_type, time_delta, notification_sent, acked, acked_ts, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        alert = (
            self.created_ts,
            self.device_id,
            self.alert_type,
            self.time_delta,
            self.notification_sent,
            self.acked,
            self.acked_ts,
            self.active)

        self.cursor.execute(sql, alert)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self

    def update(self, raw_alert: dict={}) -> bool:
        """
        Updates an alert in the `alerts` table.

        """
        self.build_from_dict(raw_alert)
        sql = """
            UPDATE alerts
            SET
                created_ts = ?,
                device_id = ?,
                alert_type = ?,
                time_delta = ?,
                notification_sent = ?,
                acked = ?,
                acked_ts = ?,
                active = ?
            WHERE id = ?"""
        the_update = (
            self.created_ts,
            self.device_id,
            self.alert_type,
            self.time_delta,
            self.notification_sent,
            self.acked,
            self.acked_ts,
            self.active,
            self.id)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def delete_device(self, device_id: int) -> bool:
        """
        Deletes all records from the `alerts` table containing a device_id, this should be
        performed when deleting a device.

        """
        sql = """DELETE FROM alerts WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

    def build_from_list(self, raw: list, build_device: bool=False):
        """
        Creates a device from a raw row record.

        """
        self.id = raw[0]
        self.created_ts = raw[1]
        self.device_id = raw[2]
        self.alert_type = raw[3]
        self.time_delta = raw[4]
        self.notification_sent = raw[5]
        self.acked = raw[6]
        self.acked_ts = raw[7]
        self.active = raw[8]

        if build_device:
            # import pdb; pdb.set_trace()∂∂∂∂∂
            self.device = Device(self.conn, self.cursor)
            self.device.get_by_id(self.device_id)


    def build_from_dict(self, raw_alert:dict):
        """
        Creates the device object from a keyed dictionary.

        """
        if 'created_ts' in raw_alert:
            self.created_ts = raw_alert['created_ts']

        if 'device_id' in raw_alert:
            self.device_id = raw_alert['device_id']

        if 'alert_type' in raw_alert:
            self.alert_type = raw_alert['alert_type']

        if 'time_delta' in raw_alert:
            self.time_delta = raw_alert['time_delta']

        if 'notification_sent' in raw_alert:
            self.notification_sent = raw_alert['notification_sent']

        if 'acked' in raw_alert:
            self.acked = raw_alert['acked']

        if 'acked_ts' in raw_alert:
            self.acked_ts = raw_alert['acked_ts']

        if 'active' in raw_alert:
            self.active = raw_alert['active']


    # def build_from_dict_new(self, raw_alert:dict):
    #     """
    #     Creates the device object from a keyed dictionary.

    #     """
    #     if 'created_ts' in raw_alert:
    #         self.created_ts = raw_alert['created_ts']

    #     if 'device_id' in raw_alert:
    #         self.device_id = raw_alert['device_id']

    #     if 'alert_type' in raw_alert:
    #         self.alert_type = raw_alert['alert_type']

    #     if 'time_delta' in raw_alert:
    #         self.time_delta = raw_alert['time_delta']

    #     if 'notification_sent' in raw_alert:
    #         self.notification_sent = raw_alert['notification_sent']

    #     if 'acked' in raw_alert:
    #         self.acked = raw_alert['acked']

    #     if 'acked_ts' in raw_alert:
    #         self.acked_ts = raw_alert['acked_ts']

    #     if 'active' in raw_alert:
    #         self.active = raw_alert['active']


# End File: lan-nanny/modules/models/alert.py
