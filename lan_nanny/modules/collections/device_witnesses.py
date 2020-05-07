"""Device Witnesses
Gets collections of Device Witnesses.

"""
from datetime import timedelta

import arrow

from .base import Base
from ..models.device_witness import DeviceWitness


class DeviceWitnesses(Base):

    def __init__(self, conn=None, cursor=None):
        """ Store Sqlite conn and model table_name as well as the model obj for the collections
            target model.
        """
        super(DeviceWitnesses, self).__init__(conn, cursor)
        self.table_name = DeviceWitness().table_name
        self.collect_model = DeviceWitness

    def get_count_since_by_device_id(self, device_id: int, seconds_since_created: int) -> int:
        """Get count of DeviceWitness instances in table created in last x minutes."""
        then = arrow.utcnow().datetime - timedelta(seconds=seconds_since_created)
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE 
                device_id=%s AND
                created_ts>"%s";
            """ % (self.table_name, device_id, then)
        self.cursor.execute(sql)
        raw_witness_count = self.cursor.fetchone()
        return raw_witness_count[0]

    def get_device_since(self, device_id, since=86400):
        then = arrow.utcnow().datetime - timedelta(seconds=since)
        sql = """
            SELECT *
            FROM `%s`
            WHERE
                `device_id` = %s AND
                `created_ts` >= "%s";
        """ % (self.table_name, device_id, then)
        self.cursor.execute(sql)
        raw_device_witness = self.cursor.fetchall()
        return raw_device_witness

    def get_by_scan_id(self, scan_id: int) -> list:
        """Get all witness records from a scan_id."""
        sql = """
            SELECT *
            FROM %s
            WHERE scan_id = %s
            ORDER BY created_ts DESC;""" % (self.table_name, scan_id)

        self.cursor.execute(sql)
        raw_witnesses = self.cursor.fetchall()
        witnesses = []
        for raw_witness in raw_witnesses:
            witness = DeviceWitness(self.conn, self.cursor)
            witness.build_from_list(raw_witness, build_device=True)
            witnesses.append(witness)
        return witnesses

    def prune(self, days: int) -> bool:
        """Method to remove data older than x days from database."""
        days_back = arrow.utcnow().datetime - timedelta(days=days)
        sql = """
            DELETE FROM %s
            WHERE created_ts <= "%s"; """ % (self.table_name, days_back)
        self.cursor.execute(sql)
        self.conn.commit()

    def delete_device(self, device_id: int) -> bool:
        """Delete all device port records for a device_id."""
        sql = """DELETE FROM %s WHERE device_id=%s""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/collections/device_witnesses.py
