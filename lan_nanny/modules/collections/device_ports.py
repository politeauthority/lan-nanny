"""Device Ports Collection.
Gets collections of device ports.

"""
from .base import Base
from ..models.device_port import DevicePort


class DevicePorts(Base):
    """Collection class for gathering groups of device ports."""

    def __init__(self, conn=None, cursor=None):
        """Store Sqlite conn and model table_name as well as the model obj for the collections
           target model.
        """
        super(DevicePorts, self).__init__(conn, cursor)
        self.table_name = DevicePort().table_name
        self.collect_model = DevicePort

    def get_by_device_id(self, device_id: int) -> list:
        """Get all devices in the database. """
        sql = """
            SELECT *
            FROM %s
            WHERE device_id=%s
            ORDER BY last_seen DESC;""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        raw_device_ports = self.cursor.fetchall()
        device_ports = self.build_from_lists(raw_device_ports, build_ports=True)

        return device_ports

    def update_device_mac_pair(self, new_device_id: int, device_mac_id: int) -> bool:
        """Update device port records when a mac address is changed to be associated to a
           different device. 

        """
        sql = """
            UPDATE `%s`
            SET `device_id` = %s
            WHERE `device_mac_id` = %s;
        """ % (self.table_name, new_device_id, device_mac_id)
        print("\n")
        print("Update Device Ports")
        print(sql)
        print("\n")
        self.cursor.execute(sql)
        return True


    def delete_device(self, device_id: int) -> bool:
        """Delete all device port records for a device_id."""
        sql = """DELETE FROM %s WHERE device_id=%s""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        return True

    def build_from_lists(self, raws: list, build_ports: bool = False) -> list:
        """
           Build a model from an ordered list, converting data types to their desired type where
           possible.
        """
        device_ports = super(DevicePorts, self).build_from_lists(raws)
        if not build_ports:
            return device_ports

        for device_port in device_ports:
            device_port.get_port()
        return device_ports


# End File: lan-nanny/lan_nanny/modules/collections/device_ports.py
