"""Alert

"""
from datetime import datetime


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
        self.alert_acked = None

    def __repr__(self):
        return "<Alert %s>" % self.id

    def get_by_id(self, device_id: int):
        """
        Gets a device from the devices table based on it's device ID.

        """
        sql = """SELECT * FROM devices WHERE id=%s""" % device_id
        self.cursor.execute(sql)
        device_raw = self.cursor.fetchone()
        if not device_raw:
            return {}
        
        self.build_from_list(device_raw)

        return self

    def create(self, raw_alert: dict={}):
        """
        Creates an alert by inserting into the `alerts` table, returning the alert object.

        """
        self.build_from_dict(raw_alert)
        

        sql = """
            INSERT INTO alerts
            (created_ts, device_id, alert_type, time_delta, notification_sent, alert_acked)
            VALUES (?, ?, ?, ?, ?, ?)"""

        alert = (
            self.created_ts,
            self.device_id,
            self.alert_type,
            self.time_delta,
            self.notification_sent,
            self.alert_acked)


        self.cursor.execute(sql, device)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self

    def update(self, raw_alert: dict={}) -> bool:
        """
        Updates an alert in the `alerts` table.

        """
        self.build_from_dict(raw_alert)
        sql = """
            UPDATE devices
            SET
                created_ts = ?,
                device_id = ?,
                alert_type = ?,
                time_delta = ?,
                notification_sent = ?,
                alert_acked = ?
            WHERE id = ?"""
        the_update = (
            self.created_ts,
            self.device_id,
            self.alert_type,
            self.time_delta,
            self.notification_sent,
            self.alert_acked
            self.id)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def build_from_list(self, raw: list):
        """
        Creates a device from a raw row record.

        """
        self.id = raw[0]
        self.created_ts = raw[1]
        self.device_id = raw[2]
        self.alert_type = raw[3]
        self.time_delta = raw[4]
        self.notification_sent = raw[5]

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


# End File: lan-nanny/modules/alert.py
