"""Devices Collection
Gets collections of devices.

"""
from datetime import timedelta

import arrow
from flask import g
from .base_entity_metas import BaseEntityMetas
from ..models.device import Device
from .. import utils


class Devices(BaseEntityMetas):
    """Collection class for gathering groups of devices."""

    def __init__(self, conn=None, cursor=None):
        """Store Sqlite conn and model table_name as well as the model obj for the collections
           target model.
        """
        super(Devices, self).__init__(conn, cursor)
        self.table_name = Device().table_name
        self.collect_model = Device

    def get_recent(self) -> list:
        """Get all devices in the database. """
        sql = """
            SELECT *
            FROM %s
            ORDER BY last_seen DESC
            LIMIT 20;""" % self.table_name
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self.build_from_lists(raw_devices)
        return devices

    def get_online_count(self) -> int:
        """Get currently online devices as an int."""
        since = int(g.options['active-timeout'].value)
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT COUNT(*)
            FROM devices
            WHERE last_seen >= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_count = self.cursor.fetchone()
        return raw_count[0]

    def get_online_unidentified_count(self) -> int:
        """Get currently online, unidentified devices as an int."""
        since = int(g.options['active-timeout'].value)
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT COUNT(*)
            FROM devices
            WHERE
                last_seen >= '%s' AND
                `identified` = 0
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_count = self.cursor.fetchone()
        return raw_count[0]


    def get_online(self, since: int) -> list:
        """Get all online devices in the database."""
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen >= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        presetines = self.build_from_lists(raws)
        return presetines

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
        devices = self.build_from_lists(raw_devices)
        return devices

    def get_favorites(self):
        """Get favorite devices in the database. """
        sql = """
            SELECT *
            FROM devices
            WHERE favorite = 1
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self.build_from_lists(raw_devices)
        return devices

    def get_new_count(self) -> int:
        """Get new devices from the last 24 hours. """
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
        """Get new devices from the last 24 hours. """
        new_since = arrow.utcnow().datetime - timedelta(hours=24)
        sql = """
            SELECT *
            FROM devices
            WHERE first_seen > "%s"
            ORDER BY last_seen DESC;""" % new_since

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self.build_from_lists(raw_devices)
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
        devices = self.build_from_lists(raw_devices)
        return devices

    def with_enabled_port_scanning(self) -> list:
        """Get devices with port_scanning enabled. """
        sql = """
            SELECT *
            FROM devices
            WHERE
                port_scan = 1
            ORDER BY last_port_scan DESC;"""
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = self.build_from_lists(raw_devices)
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
        devices = self.get_by_ids(device_ids)
        return devices

    def search(self, phrase: str) -> list:
        """Device search method, currently checks against device name, mac, ip and vendor."""
        name_sql = utils.gen_like_sql('name', phrase)
        ip_sql = utils.gen_like_sql('ip', phrase)
        vendor_sql = utils.gen_like_sql('vendor', phrase)
        notes_sql = utils.gen_like_sql('notes', phrase)
        type_sql = utils.gen_like_sql('kind', phrase)
        sql = """
            SELECT *
            FROM devices
            WHERE
                %(name)s OR
                %(ip)s OR
                %(vendor)s OR
                %(type)s; """ % {
            'name': name_sql,
            'ip': ip_sql,
            'vendor': vendor_sql,
            'type': type_sql}

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        raw_devices_from_mac = self._search_device_macs(phrase)
        raw_devices_from_notes = self._search_device_notes(phrase)
        raw_devices = raw_devices + raw_devices_from_mac + raw_devices_from_notes

        raw_devices = utils.remove_dupicates(raw_devices)

        devices = self.build_from_lists(raw_devices)
        return devices

    def _search_device_macs(self, phrase) -> list:
        """Search DeviceMacs for a matching mac address phrase from a search param, returning the
           raw devices if there is such a match.
        """
        mac_sql = utils.gen_like_sql('mac_addr', phrase)
        ip_sql = utils.gen_like_sql('ip_addr', phrase)
        sql = """
            SELECT *
            FROM device_macs
            WHERE
                %s OR
                %s
            """ % (mac_sql, ip_sql)

        self.cursor.execute(sql)
        raw_device_macs = self.cursor.fetchall()

        if not raw_device_macs:
            return []

        device_ids = []
        for raw_device_mac in raw_device_macs:
            device_ids.append(raw_device_mac[0])

        sql = """
            SELECT *
            FROM devices
            WHERE `id` IN(%s);
        """ % utils.gen_sql_list(device_ids)
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        return raw_devices

    def _search_device_notes(self, phrase) -> list:
        """Search entity_metaas device notes for the given phrase. """
        notes_sql = utils.gen_like_sql('value', phrase)
        sql = """
            SELECT entity_id
            FROM `entity_metas`
            WHERE
                `entity_type` = "devices" AND
                `name` = "notes" AND
                %s
            """ % (notes_sql)

        self.cursor.execute(sql)
        raw_device_notes = self.cursor.fetchall()

        if not raw_device_notes:
            return []

        device_ids = []
        for raw_device_note in raw_device_notes:
            device_ids.append(raw_device_note[0])

        sql = """
            SELECT *
            FROM devices
            WHERE `id` IN(%s);
        """ % utils.gen_sql_list(device_ids)
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()

        return raw_devices

    def get_w_alerts(self, alerts: list) -> dict:
        """Get a collection of Devices from the list Alert objects supplied."""
        alert_device_ids = []
        for alert_obj in alerts:
            if 'device' in alert_obj.metas:
                device_id = int(alert_obj.metas['device'].value)
                if device_id not in alert_device_ids:
                    alert_device_ids.append(device_id)
        devices = {}
        if alert_device_ids:
            devices = self.get_by_ids_keyed(alert_device_ids)
        return devices

    def build_from_lists(self, raws: list, meta: bool = False, build_ports: bool = False) -> list:
        """Build a model from an ordered list, converting data types to their desired type where
           possible.

           :param raws: Raw data to convert into model objects.
           :param build_ports: Build the Device's Ports
        """
        devices = super(Devices, self).build_from_lists(raws, meta=meta)
        if not build_ports:
            return devices
        for device in devices:
            device.get_ports()
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
