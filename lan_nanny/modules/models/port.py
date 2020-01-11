"""Port Model

"""
from .base import Base


class Port(Base):

    def __init__(self, conn=None, cursor=None):
        super(Port, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'Port'
        self.table_name = 'ports'

        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int'
            },
            {
                'name': 'port',
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
                'name': 'service_name',
                'type': 'str'
            },
            {
                'name': 'custom_service_name',
                'type': 'str'
            },
            {
                'name': 'protocol',
                'type': 'str'
            },
            {
                'name': 'updated_ts',
                'type': 'datetime'
            }
        ]
        self.setup()

    def __repr__(self):
        return "<Port %s>" % self.id

    def get_by_device_port_protocol(
        self,
        device_id: int=None,
        port_number: str=None,
        protocol: str=None):
        """
        """
        if not device_id and self.device_id:
            device_id = self.device_id

        if not port_number and self.port:
            port_number = self.port

        if not protocol and self.protocol:
            protocol = self.protocol

        sql = """
        SELECT *
        FROM ports
        WHERE
            device_id = ? AND
            port = ? AND
            protocol = ?
        LIMIT 1"""

        vals = (device_id, port_number, protocol)
        self.cursor.execute(sql, vals)
        port_raw = self.cursor.fetchone()
        if not port_raw:
            return False

        self.build_from_list(port_raw)
        return True

    def get_by_port_number(self, port_number):
        sql = """
        SELECT *
        FROM ports
        WHERE
            port = %s""" % port_number
        vals = (port_number)
        print(sql)
        self.cursor.execute(sql)
        port_raw = self.cursor.fetchone()
        if not port_raw:
            return False

        self.build_from_list(port_raw)

# End File: lan-nanny/lan_nanny/modules/models/port.py
