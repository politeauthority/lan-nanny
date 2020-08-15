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

# End File: lan-nanny/lan_nanny/modules/collections/device_macs.py
