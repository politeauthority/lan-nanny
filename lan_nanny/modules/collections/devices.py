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

    def get_online(self, since: datetime) -> list:
        """
        Gets all devices in the database.

        """
        sql = """
            SELECT *
            FROM devices
            WHERE last_seen >= '%s'
            ORDER BY last_seen DESC;""" % since

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
        Gets Devices with alerts_online OR alerts_offline

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
                last_port_scan <= '%s'
            ORDER BY last_port_scan ASC %s;""" % (hours_24, limit)
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices


# End File: lan-nanny/modules/collections/devices.py
