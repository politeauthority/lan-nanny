"""Device

"""
from datetime import datetime

import arrow


class Device():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.mac = None
        self.vendor = None
        self.ip = None
        self.last_seen = None
        self.first_seen = None
        self.name = None
        self.hide = None
        self.favorite = 0
        self.icon = None
        self.alert_online = 0
        self.alert_offline = 0
        self.alert_delta = None
        self.port_scan = None
        self.last_port_scan = None
        self.update_ts = None

    def __repr__(self):
        if self.name:
            return "<Device %s>" % self.name
        return "<Device %s>" % self.mac

    def get_by_mac(self, mac: str):
        """
        Gets a device from the devices table based on mac address.

        """
        sql = """SELECT * FROM devices WHERE mac='%s'""" % mac
        self.cursor.execute(sql)
        device_raw = self.cursor.fetchone()
        if not device_raw:
            return self

        self.build_from_list(device_raw)

        return self

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

    def create(self, scan_time: datetime, raw_device: dict={}):
        """
        Creates a device by inserting into the devices table, returning its new key.

        """
        self.build_from_dict(raw_device)

        self.last_seen = scan_time
        self.first_seen = scan_time
        if not self.name:
            self.name = self.vendor


        self._set_icon()
        self.update_ts = arrow.utcnow().datetime

        sql = """
            INSERT INTO devices
            (mac, vendor, last_ip, last_seen, first_seen, name, hide, favorite, icon, alert_online,
            alert_offline, alert_delta, port_scan, last_port_scan, update_ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        device = (
            self.mac,
            self.vendor,
            self.ip,
            self.last_seen,
            self.first_seen,
            self.name,
            self.hide,
            self.favorite,
            self.icon,
            self.alert_online,
            self.alert_offline,
            self.alert_delta,
            self.port_scan,
            self.last_port_scan,
            self.update_ts)

        self.cursor.execute(sql, device)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self

    def update(self, raw_device: dict={}) -> bool:
        """
        Updates a device in the `devices` table setting its new last seen time to the scan time.

        """
        self.build_from_dict(raw_device)
        self.update_ts = arrow.utcnow().datetime
        sql = """
            UPDATE devices
            SET
                mac = ?,
                vendor = ?,
                last_ip = ?,
                last_seen = ?,
                first_seen = ?,
                name = ?,
                hide = ?,
                favorite = ?,
                icon = ?,
                alert_online = ?,
                alert_offline = ?,
                alert_delta = ?,
                port_scan = ?,
                last_port_scan = ?,
                update_ts = ?
            WHERE id = ?"""
        the_update = (
            self.mac,
            self.vendor,
            self.ip,
            self.last_seen,
            self.first_seen,
            self.name,
            self.hide,
            self.favorite,
            self.icon,
            self.alert_online,
            self.alert_offline,
            self.alert_delta,
            self.port_scan,
            self.last_port_scan,
            self.update_ts,
            self.id)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def delete(self) -> bool:
        """
        Deletes a device from the `devices` table.

        """
        sql = """DELETE FROM devices WHERE id = %s """ % self.id
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def build_from_list(self, raw: list):
        """
        Creates a device from a raw row record.

        """
        self.id = raw[0]
        self.mac = raw[1]
        self.vendor = raw[2]
        self.ip =  raw[3]
        self.last_seen = raw[4]
        if self.last_seen:
            self.last_seen = arrow.get(self.last_seen).datetime
        self.first_seen = raw[5]
        self.name = raw[6]
        self.hide = raw[7]
        self.favorite = raw[8]
        self.icon = raw[9]
        self.alert_online = raw[10]
        self.alert_offline = raw[11]
        self.alert_delta = raw[12]
        self.port_scan = raw[13]
        self.last_port_scan = raw[14]
        self.update_ts = raw[15]

    def build_from_dict(self, raw_device:dict):
        """
        Creates the device object from a keyed dictionary.

        """
        if 'ip' in raw_device:
            self.ip = raw_device['ip']

        if 'mac' in raw_device:
            self.mac = raw_device['mac']

        if 'vendor' in raw_device:
            self.vendor = raw_device['vendor']

        if 'name' in raw_device:
            self.name = raw_device['name']

        if 'hide' in raw_device:
            self.hide = raw_device['hide']

        if 'favorite' in raw_device:
            self.favorite = raw_device['favorite']

        if 'icon' in raw_device:
            self.hide = raw_device['hide']

        if 'alert_online' in raw_device:
            self.alert_online = raw_device['alert_online']

        if 'alert_offline' in raw_device:
            self.alert_offline = raw_device['alert_offline']

        if 'alert_delta' in raw_device:
            self.alert_delta = raw_device['alert_delta']

        if 'port_scan' in raw_device:
            self.port_scan = raw_device['port_scan']

        if 'last_port_scan' in raw_device:
            self.last_port_scan = raw_device['last_port_scan']

        if 'update_ts' in raw_device:
            self.update_ts = raw_device['update_ts']

    def _set_icon(self):
        """
        Attempts to set a device icon.

        """
        if self.icon:
            return

        if self.vendor == "Apple":
            self.icon = "fab fa-apple"

        if not self.name:
            self.icon = "fas fa-question"

# End File: lan-nanny/modules/models/device.py
