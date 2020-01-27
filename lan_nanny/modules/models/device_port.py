"""DevicePorts Model

"""
from .base import Base


class DevicePort(Base):

    def __init__(self, conn=None, cursor=None):
        super(DevicePort, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'device_ports'

        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int'
            },
            {
                'name': 'port_id',
                'type': 'int'
            },
            {
                'name': 'last_seen',
                'type': 'datetime'
            },
            {
                'name': 'status',
                'type': 'str'
            },
            {
                'name': 'updated_ts',
                'type': 'datetime'
            }
        ]
        self.port = None
        self.setup()

    def __repr__(self):
        return "<DevicePort %s>" % self.id

    def get_by_device_and_port(self, device_id: int=None, port_id: int=None):
        """Get a DevicePort by device_id and port_id."""
        if not device_id and self.device_id:
            device_id = self.device_id

        if not port_id and self.port_id:
            port_id = self.port_id

        sql = """
        SELECT *
        FROM device_ports
        WHERE
            device_id = ? AND
            port_id = ?
        LIMIT 1"""

        vals = (device_id, port_id)
        self.cursor.execute(sql, vals)
        device_port_raw = self.cursor.fetchone()
        if not device_port_raw:
            return False

        self.build_from_list(device_port_raw)
        return True

# End File: lan-nanny/lan_nanny/modules/models/device_port.py
