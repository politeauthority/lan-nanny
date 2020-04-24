"""Alerts Collection
Gets collections of alerts.

"""
from .base import Base
from ..models.alert import Alert
from .base_entity_metas import BaseEntityMetas


class Alerts(BaseEntityMetas):

    def __init__(self, conn=None, cursor=None):
        super(Alerts, self).__init__(conn, cursor)
        self.table_name = Alert().table_name
        self.collect_model = Alert

    def get_firing(self, build_devices=False) -> list:
        """Gets all active alerts from the database."""

        sql = """
            SELECT *
            FROM %s
            WHERE active = 1
            ORDER BY created_ts DESC;""" % (self.table_name)

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = self.build_from_lists(raw_alerts)
        return alerts

    def get_recent(self, build_devices=False) -> list:
        """Gets all active alerts from the database."""

        sql = """
            SELECT *
            FROM %s
            WHERE active = 0
            ORDER BY created_ts DESC
            LIMIT 10;""" % (self.table_name)

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = self.build_from_lists(raw_alerts)
        return alerts

    def get_active_unacked_num(self) -> int:
        """Gets all active, unacked alerts number from the database."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                active = 1 AND
                acked = 0
            ORDER BY created_ts DESC;""" % (self.table_name)
        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        return len(raw_alerts)

    def get_for_device(self, device_id: int) -> list:
        """Get all alert objects for a single device."""
        sql = """
            SELECT entity_id
            FROM %s
            WHERE
                entity_type="alerts" AND
                name="device" AND
                value=%s;
        """ % ("entity_metas", device_id)
        self.cursor.execute(sql)
        raw_metas = self.cursor.fetchall()
        alert_ids = []
        for raw in raw_metas:
            alert_ids.append(raw[0])
        if not alert_ids:
            return []

        alerts = self.get_by_ids(alert_ids)
        return alerts

    def delete_device(self, device_id: int) -> bool:
        """Delete all device alert records for a device_id."""
        device_alerts = self.get_for_device(device_id)
        for da in device_alerts:
            da.delete()
        return True


# End File: lan-nanny/lan_nanny/modules/collections/alerts.py
