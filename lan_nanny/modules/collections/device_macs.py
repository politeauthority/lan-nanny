"""Device Macs Collection.
Gets collections of device macs.

"""
from .base import Base
from ..models.device_mac import DeviceMac


class DeviceMacs(Base):
    """Collection class for gathering groups of device macs."""

    def __init__(self, conn=None, cursor=None):
        """Store database conn/connection and model table_name as well as the model obj for the 
           collections target model.
        """
        super(DeviceMacs, self).__init__(conn, cursor)
        self.table_name = DeviceMac().table_name
        self.collect_model = DeviceMac

    def get_by_device_id(self, device_id: int) -> list:
        """Get all device's macs in the database. """
        sql = """
            SELECT *
            FROM %s
            WHERE device_id=%s
            ORDER BY last_seen DESC;""" % (self.table_name, device_id)
        self.cursor.execute(sql)
        raw_device_macs = self.cursor.fetchall()
        device_macs = self.build_from_lists(raw_device_macs)

        return device_macs

    def get_all_macs_with_device_name(self):
        all_macs = self.get_all()

        ret = []
        for mac in all_macs:
            mac_tmp = {
                'id': mac.id,
                'mac_addr': mac.mac_addr,
                'ip_addr': mac.ip_addr,
                'device_name': self.get_device_name_from_device_id(mac.device_id)
            }
            ret.append(mac_tmp)
        print("\n")
        print(ret)
        print("\n")
        return ret
        # all_devices = Devices(self.conn, self.cursor).get_all()

    def get_device_name_from_device_id(self, device_id: int):
        """Get the name of a device by the device_id. We can't import the Device model here due to
           circular dependency issues, and since this is just a one off for the
           get_all_macs_with_device_name method we just do it here.
        """
        sql = """
            SELECT name
            FROM devices
            WHERE id=%s;
        """ % device_id
        self.cursor.execute(sql)
        raw_device_name = self.cursor.fetchone()
        return raw_device_name[0]

# End File: lan-nanny/lan_nanny/modules/collections/device_macs.py
