"""Port Model

"""
from .base import Base


class Port(Base):

    def __init__(self, conn=None, cursor=None):
        super(Port, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'ports'

        self.field_map = [
            {
                'name': 'port',
                'type': 'str'
            },
            {
                'name': 'protocol',
                'type': 'str'
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
                'name': 'service',
                'type': 'str'
            },
            {
                'name': 'num_devices',
                'type': 'int',
                'default': 0,
            },
            {
                'name': 'updated_ts',
                'type': 'datetime'
            }
        ]
        self.devices = []
        self.setup()

    def __repr__(self):
        return "<Port %s>" % self.id

    def get_by_port_and_protocol(self, port_number: str=None, protocol: str=None) -> bool:
        """Get a Port obj by port number and protocol."""
        if not port_number and self.port:
            port_number = self.port

        if not protocol and self.protocol:
            protocol = self.protocol

        sql = """
        SELECT *
        FROM ports
        WHERE
            port = ? AND
            protocol = ?
        LIMIT 1"""

        vals = (port_number, protocol)
        self.cursor.execute(sql, vals)
        port_raw = self.cursor.fetchone()
        if not port_raw:
            return False

        self.build_from_list(port_raw)
        return True

# End File: lan-nanny/lan_nanny/modules/models/port.py
