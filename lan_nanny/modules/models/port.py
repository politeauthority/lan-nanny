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
                'name': 'updated_ts',
                'type': 'datetime'
            }
        ]
        self.setup()

    def __repr__(self):
        return "<Port %s>" % self.id

# End File: lan-nanny/modules/models/port.py
