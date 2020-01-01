"""Alerts
Gets collections of alerts.

"""
from ..models.alert import Alert


class Alerts():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all(self) -> list:
        """
        Gets all alerts from the `alerts` table.

        """
        sql = """
            SELECT *
            FROM alerts
            ORDER BY created_ts DESC;"""

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = []
        for raw_alert in raw_alerts:
            alert = Alert(self.conn, self.cursor)
            alert.build_from_list(raw_alert, build_device=True)
            alerts.append(alert)
        return alerts

    def get_active(self, build_devices: bool=False) -> list:
        """
        Gets all active alerts from the `alerts` table.

        """
        sql = """
            SELECT *
            FROM alerts
            WHERE active = 1
            ORDER BY created_ts DESC;"""

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = []
        for raw_alert in raw_alerts:
            alert = Alert(self.conn, self.cursor)
            alert.build_from_list(raw_alert, build_devices)
            alerts.append(alert)
        return alerts

    def get_active_unacked(self, build_devices: bool=False) -> list:
        """
        Gets all active alerts from the `alerts` table.

        """
        sql = """
            SELECT *
            FROM alerts
            WHERE
                active = 1 AND
                acked = 0
            ORDER BY created_ts DESC;"""

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = []
        for raw_alert in raw_alerts:
            alert = Alert(self.conn, self.cursor)
            alert.build_from_list(raw_alert, build_device=build_devices)
            alerts.append(alert)
        return alerts

# End File: lan-nanny/modules/collections/alerts.py
