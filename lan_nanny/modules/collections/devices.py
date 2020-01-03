"""Devices
Gets collections of devices.

"""
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

    def get_favorites(self):
        """
        Gets all devices in the database.

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

# End File: lan-nanny/modules/collections/devices.py
