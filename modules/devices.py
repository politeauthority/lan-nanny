"""Devices

"""
from datetime import datetime

from .device import Device

class Devices():

    def __init__(self):
        self.conn = None
        self.cursor = None

    def get_all(self):
        """
        Gets all devices in the database.

        """
        sql = "SELECT * FROM devices;"
        self.cursor.execute(sql)
        raw_devices = self.cursor.fetchall()
        devices = []
        for raw_device in raw_devices:
            device = Device()
            device.build_from_list(raw_device)
            devices.append(device)
        return devices

# End File: lan-nanny/modules/devices.py
