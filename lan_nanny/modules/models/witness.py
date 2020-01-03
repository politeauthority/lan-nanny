"""Witness Model

"""
from .base import Base


class Witness(Base):

    def __init__(self, conn=None, cursor=None):
        super(Witness, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'Witness'
        self.table_name = 'witness'

        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int'
            },
            {
                'name': 'run_id',
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

    def __repr__(self):
        return "<Witness %s>" % self.id

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

    def delete_device(self, device_id: int) -> bool:
        """
        Deletes all records from the `witness` table containing a device_id, this should be
        performed when deleting a device.

        """
        sql = """DELETE FROM witness WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/modules/models/witness.py
