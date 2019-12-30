"""Port Model

"""
from datetime import datetime

import arrow


class Port():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.device_id = None
        self.port = None
        self.last_seen = None
        self.status = None
        self.service_name = None
        self.update_ts = None

    def __repr__(self):
        return "<Port %s>" % self.id

    def get_by_id(self, port_id: int):
        """
        Gets a port from the `ports` table based on it's port ID.

        """
        sql = """SELECT * FROM ports WHERE id=%s""" % port_id
        self.cursor.execute(sql)
        device_raw = self.cursor.fetchone()
        if not device_raw:
            return {}
        
        self.build_from_list(device_raw)

        return self

    def create(self,scan_time: datetime, raw_port: dict={}):
        """
        Creates a port by inserting into the `ports` table, returning its new key.

        """
        self.build_from_dict(raw_device)
        self.last_seen = scan_time
        self.update_ts = arrow.utcnow().datetime

        sql = """
            INSERT INTO devices
            (device_id,  port,  last_seen, status, service_name, update_ts)
            VALUES (?, ?, ?, ?, ?, ?)"""

        device = (
            self.device_id,
            self.port,
            self.last_seen,
            self.status,
            self.service_name,
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
                device_id = ?,
                port = ?,
                last_seen = ?,
                status = ?,
                service_name = ?,
                update_ts = ?
            WHERE id = ?"""
        the_update = (
            self.device_id,
            self.port,
            self.last_seen,
            self.status,
            self.service_name,
            self.update_ts,
            self.id)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def build_from_list(self, raw: list):
        """
        Creates a device from a raw row record.

        """
        self.id = raw[0]
        self.device_id = raw[1]
        self.last_seen = raw[2]
        self.status =  raw[3]
        self.service_name = raw[4]
        self.update_ts = raw[5]

    def build_from_dict(self, raw_device:dict):
        """
        Creates the device object from a keyed dictionary.

        """
        if 'device_id' in raw_device:
            self.device_id = raw_device['device_id']

        if 'last_seen' in raw_device:
            self.last_seen = raw_device['last_seen']

        if 'status' in raw_device:
            self.status = raw_device['status']

        if 'service_name' in raw_device:
            self.service_name = raw_device['service_name']

        if 'update_ts' in raw_device:
            self.update_ts = raw_device['update_ts']

# End File: lan-nanny/modules/models/port.py
