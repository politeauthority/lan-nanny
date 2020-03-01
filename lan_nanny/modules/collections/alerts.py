"""Alerts
Gets collections of alerts.

"""
from .base import Base
from ..models.alert import Alert
from .entity_metas import EntityMetas


class Alerts(Base):

    def __init__(self, conn=None, cursor=None):
        super(Alerts, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = Alert().table_name
        self.collect_model = Alert

    def get_active(self) -> list:
        """Gets all active alerts from the database."""

        sql = """
            SELECT *
            FROM %s
            WHERE active = 1
            ORDER BY created_ts DESC;""" % (self.table_name)

        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = self.build_models_from_list(raw_alerts)
        return alerts

    def get_active_unacked(self, build_devices: bool=False) -> list:
        """Gets all active, unacked alerts from the database."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                active = 1 AND
                acked = 0
            ORDER BY created_ts DESC;""" % (self.table_name)
        self.cursor.execute(sql)
        raw_alerts = self.cursor.fetchall()
        alerts = self.build_models_from_list(raw_alerts)
        return alerts

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
        # sql = """DELETE FROM %s WHERE device_id=%s""" % (self.table_name, device_id)
        # self.cursor.execute(sql)
        # print(sql)

        # sql = """
        #     DELETE FROM entity_metas 
        #     WHERE
        #         entity_type="device" AND
        #         value="%s"; """ % (device_id)
        # self.cursor.execute(sql)
        # print(sql)
        return True


# End File: lan-nanny/lan_nanny/modules/collections/alerts.py
