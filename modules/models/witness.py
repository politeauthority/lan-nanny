"""Witness

"""
from datetime import datetime


class Witness():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.device_id = None
        self.run_id = None
        self.witness_ts = None

    def __repr__(self):
        return "<Witness %s>" % self.id

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

    def create(self, raw_witness: dict={}):
        """
        Creates a witness by inserting into the `witness` table, returning the Witness object.

        """
        self.build_from_dict(raw_witness)

        sql = """
            INSERT INTO witness
            (device_id, run_id, witness_ts)
            VALUES (?, ?, ?)"""

        witness = (
            self.device_id,
            self.run_id,
            self.witness_ts)

        self.cursor.execute(sql, witness)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self

    def get_device_for_scan(self, device_id: int, scan_id: int) -> bool:
        """
        Checks the witness table for a device's presence in a particular scan. If the device was in
        the requested scan, returns True, otherwise False.

        """
        sql = """
            SELECT *
            FROM witness
            WHERE
                device_id=? AND
                run_id = ?
        """
        var = (device_id, scan_id)

        self.cursor.execute(sql, var)
        witness_record = self.cursor.fetchone()
        if witness_record:
            return True
        return False

    def get_device_last_online(self, device_id: int) -> bool:
        """
        Checks the witness table for the last witness of a device online.

        """
        sql = """
            SELECT *
            FROM witness
            WHERE
                device_id=?
            ORDER BY witness_ts DESC
        """
        var = (device_id)

        self.cursor.execute(sql, var)
        witness_raw = self.cursor.fetchone()
        witness = self.build_from_list(witness_raw)
        if witness:
            return witness
        return False

    def delete_device(self, device_id: int) -> bool:
        """
        Deletes all records from the `witness` table containing a device_id, this should be
        performed when deleting a device.

        """
        sql = """DELETE FROM witness WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

    def build_from_list(self, raw: list):
        """
        Creates a witness from a raw row record.

        """
        self.id = raw[0]
        self.device_id = raw[1]
        self.run_id = raw[2]
        self.witness_ts = raw[3]

    def build_from_dict(self, raw_witness:dict):
        """
        Creates the witness object from a keyed dictionary.

        """
        if 'device_id' in raw_witness:
            self.device_id = raw_witness['device_id']

        if 'run_id' in raw_witness:
            self.run_id = raw_witness['run_id']

        if 'witness_ts' in raw_witness:
            self.witness_ts = raw_witness['witness_ts']


# End File: lan-nanny/modules/models/witness.py
