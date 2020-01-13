"""Devices
Gets collections of devices.

"""
from datetime import datetime, timedelta

import arrow

from ..models.device import Device


class Devices():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all(self) -> list:
        """
        Gets all devices in the database.

        """
        sql = """
            SELECT *
            FROM devices
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices

    def get_online(self, since: int) -> list:
        """
        Gets all online devices in the database.

        """
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen >= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices


    def get_offline(self, since: int) -> list:
        """
        Gets all offline devices in the database.

        """
        last_online = arrow.utcnow().datetime - timedelta(minutes=since)
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen <= '%s'
            ORDER BY last_seen DESC;""" % last_online

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices


    def get_favorites(self):
        """
        Gets favorite devices in the database.

        """
        sql = """
            SELECT *
            FROM devices
            WHERE favorite = 1
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices

    def with_alerts_on(self):
        """
        Gets Devices with alerts_online OR alerts_offline

        """
        sql = """
            SELECT *
            FROM devices
            WHERE
                alert_online = 1 OR
                alert_offline = 1
            ORDER BY last_seen DESC;"""

        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices

    def for_port_scanning(self, limit: int=None):
        """
        Gets Devices with port_scan enabled and either have never had a port scan, or their port
        scan was done x time ago and should be run again.

        """
        hours_24 = arrow.utcnow().datetime - timedelta(hours=24)
        limit = ''
        if limit:
            "LIMIT %s" % limit
        sql = """
            SELECT *
            FROM devices
            WHERE
                port_scan = 1 AND
                (
                    last_port_scan <= '%s' OR
                    last_port_scan is NULL OR
                    flagged_for_scan = 1)
            ORDER BY last_port_scan ASC %s;""" % (hours_24, limit)
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device(self.conn, self.cursor)
            device.build_from_list(raw_device, build_ports=True)
            devices.append(device)
        return devices

    def get_with_open_port(self, port):
        sql = """
            SELECT device_id
            FROM ports
            WHERE
                port = %s AND
                status = 'open' """ % (port)
        self.cursor.execute(sql)
        raw_device_ids = self.cursor.fetchall()
        devices = []
        for raw_device in raw_device_ids:
            device = Device(self.conn, self.cursor)
            device.get_by_id(raw_device[0])
            devices.append(device)
        return devices

    def search(self, phrase):
        """

        """
        name_sql = self._gen_like_sql('name', phrase)
        mac_sql = self._gen_like_sql('mac', phrase)
        ip_sql = self._gen_like_sql('ip', phrase)
        vendor_sql = self._gen_like_sql('vendor', phrase)
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
        devices = []
        for raw_device in raw_devices:
            device = Device(self.conn, self.cursor)
            device.build_from_list(raw_device)
            devices.append(device)
        return devices

    def _gen_like_sql(self, field, phrase):
        return field + """ LIKE '%""" + phrase + """%' """

# End File: lan-nanny/modules/collections/devices.py
