"""Device Witness Model

"""
from .base import Base
from .device import Device


class DeviceWitness(Base):

    def __init__(self, conn=None, cursor=None):
        super(DeviceWitness, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'device_witness'

        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int'
            },
            {
                'name': 'scan_id',
                'type': 'int'
            },
            {
                'name': 'completed',
                'type': 'bool'
            },
            {
                'name': 'success',
                'type': 'bool'
            },
            {
                'name': 'num_devices',
                'type': 'str'
            },
            {
                'name': 'scan_name',
                'type': 'str'
            }
        ]
        self.setup()
        self.device = None

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
                scan_id = ?
        """
        var = (device_id, scan_id)

        self.cursor.execute(sql, var)
        witness_record = self.cursor.fetchone()
        if witness_record:
            return True
        return False

    def build_from_list(self, raw: list, build_device: bool=True):
        """
        Builds a witness from list
        @todo: should be redone to use parent for initial load and this class for device load.

        """
        c = 0
        for field in self.total_map:
            setattr(self, field['name'], raw[c])
            c += 1
        if build_device:
            self.device = Device(self.conn, self.cursor)
            self.device.get_by_id(self.device_id)

        return True

# End File: lan-nanny/lan_nanny/modules/models/device_witness.py
