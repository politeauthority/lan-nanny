"""Scan Ports Collection
Gets collections of scan port scan logs.

"""
from .base import Base
from ..models.scan_port import ScanPort


class ScanPorts(Base):

    def __init__(self, conn=None, cursor=None):
        super(ScanPorts, self).__init__(conn, cursor)
        self.table_name = ScanPort().table_name
        self.collect_model = ScanPort

    def get_by_device_id(self, device_id: int, limit=10) -> list:
        """Get a collection of ScanPorts by Device id."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                device_id=%s
            ORDER BY created_ts DESC
            LIMIT %s;
        """ % (self.table_name, device_id, limit)
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        presetines = self.build_from_lists(raws)
        return presetines

    def update_device_mac_pair(self, new_device_id: int, device_mac_id: int) -> bool:
        """Update scan ports records when a mac address is changed to be associated to a
           different device. 

        """
        sql = """
            UPDATE `%s`
            SET `device_id` = %s
            WHERE `device_mac_id` = %s;
        """ % (self.table_name, new_device_id, device_mac_id)
        print("\n")
        print("Update Scan Ports")
        print(sql)
        print("\n")
        self.cursor.execute(sql)
        return True

    def delete_device(self, device_id: int) -> bool:
        """Delete all device port records for a device_id."""
        sql = """DELETE FROM %s WHERE device_id=%s""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/collections/scan_ports.py
