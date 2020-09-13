"""DeviceMac Model

"""
from .base import Base
from .port import Port


class DeviceMac(Base):

    def __init__(self, conn=None, cursor=None):
        super(DeviceMac, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'device_macs'

        self.field_map = [
            {
                'name': 'device_id',
                'type': 'int'
            },
            {
                'name': 'addr',
                'type': 'str'
            },
            {
                'name': 'last_seen',
                'type': 'datetime'
            }
        ]
        self.setup()

    def __repr__(self):
        return "<DeviceMac %s>" % self.id


# End File: lan-nanny/lan_nanny/modules/models/device_mac.py
