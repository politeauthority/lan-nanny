"""Devices Collection
Gets collections of devices.

"""
from datetime import timedelta

import arrow

from .base import Base
from ..models.device import Device
from .. import utils


class Devices(Base):
    """ Collection class for gathering groups of devices."""

    def __init__(self, conn=None, cursor=None):
        """ Store Sqlite conn and model table_name as well as the model obj for the collections
            target model.
        """
        super(Devices, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = Device().table_name
        self.collect_model = Device
        

    def get_recent(self) -> list:
        """Get all devices in the database."""
        sql = """
            SELECT *
            FROM %s
            ORDER BY last_seen DESC
            LIMIT 20;""" % self.table_name
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def get_online(self, since: int) -> list:
        """Get all online devices in the database."""
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen >= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def get_offline(self, since: int) -> list:
        """Get all offline devices in the database."""
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen <= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def get_favorites(self):
        """Get favorite devices in the database."""
        sql = """
            SELECT *
            FROM devices
            WHERE favorite = 1
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def get_new_count(self) -> int:
        """Get new devices from the last 24 hours."""
        new_since = arrow.utcnow().datetime - timedelta(hours=24)
        sql = """
            SELECT count(*)
            FROM devices
            WHERE first_seen > "%s"
            ORDER BY last_seen DESC;""" % new_since

        self.cursor.execute(sql)
        raw_count = self.cursor.fetchone()
        return raw_count[0]

    def get_new(self) -> int:
        """Get new devices from the last 24 hours."""
        new_since = arrow.utcnow().datetime - timedelta(hours=24)
        sql = """
            SELECT *
            FROM devices
            WHERE first_seen > "%s"
            ORDER BY last_seen DESC;""" % new_since

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def with_alerts_on(self):
        """Get Devices with alerts_online OR alerts_offline."""
        sql = """
            SELECT *
            FROM devices
            WHERE
                alert_online = 1 OR
                alert_offline = 1
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def with_enabled_port_scanning(self) -> list:
        """Get devices with port_scanning enabled."""
        sql = """
            SELECT *
            FROM devices
            WHERE
                port_scan = 1
            ORDER BY last_port_scan DESC;"""
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def get_with_open_port(self, port_id: int) -> list:
        """Get devices with a specific port open."""
        sql = """
            SELECT device_id
            FROM device_ports
            WHERE
                port_id = %s AND
                state = 'open' """ % (port_id)
        self.cursor.execute(sql)
        raw_device_ids = self.cursor.fetchall()
        device_ids = []
        for raw_device_id in raw_device_ids:
            device_ids.append(raw_device_id[0])

        devices = self.get_by_device_ids(device_ids)

        return devices

    def get_by_device_ids(self, port_ids: list) -> list:
        """Get ports by a list of port IDs."""
        port_ids_sql = ""
        for port_id in port_ids:
            port_ids_sql += "%s," % port_id
        port_ids_sql = port_ids_sql[:-1]
        sql = """
            SELECT *
            FROM devices
            WHERE id IN(%s);""" % (port_ids_sql)
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def search(self, phrase: str) -> list:
        """Device search method, currently checks against device name, mac, ip and vendor."""
        name_sql = utils.gen_like_sql('name', phrase)
        mac_sql = utils.gen_like_sql('mac', phrase)
        ip_sql = utils.gen_like_sql('ip', phrase)
        vendor_sql = utils.gen_like_sql('vendor', phrase)
        sql = """
            SELECT *
            FROM devices
            WHERE
            %(name)s OR
            %(mac)s OR
            %(ip)s OR
            %(vendor)s""" % {
            'name': name_sql,
            'mac': mac_sql,
            'ip': ip_sql,
            'vendor': vendor_sql}

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self._build_raw_devices(raw_devices)
        return devices

    def _build_raw_devices(self, raw_devices, build_ports=False) -> list:
        """Build raw devices into a list of fully built device objects."""
        devices = []
        for raw_device in raw_devices:
            device = Device(self.conn, self.cursor)
            device.build_from_list(raw_device, build_ports=build_ports)
            devices.append(device)
        return devices

    def _get_device_field_map(self, append_table_name=False) -> list:
        """Get flattened table for a model as a list with just field names."""
        device = Device()
        fields = []
        for field in device.total_map:
            if append_table_name:
                fields.append("devices.%s" % field['name'])
            else:
                fields.append(field['name'])
        return fields


# End File: lan-nanny/modules/collections/devices.py
