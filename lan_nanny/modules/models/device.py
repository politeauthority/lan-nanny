"""Device Model

"""
import arrow

from .base import Base


class Device(Base):

    def __init__(self, conn=None, cursor=None):
        super(Device, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.model_name = 'Device'
        self.table_name = 'devices'

        self.field_map = [
            {
                'name': 'mac',
                'type': 'str',
            },
            {
                'name': 'vendor',
                'type': 'str'
            },
            {
                'name': 'ip',
                'type': 'str'
            },
            {
                'name': 'last_seen',
                'type': 'datetime'
            },
            {
                'name': 'first_seen',
                'type': 'datetime'
            },
            {
                'name': 'name',
                'type': 'str'
            },
            {
                'name': 'hide',
                'type': 'bool'
            },
            {
                'name': 'favorite',
                'type': 'bool'
            },
            {
                'name': 'icon',
                'type': 'str'
            },
            {
                'name': 'alert_online',
                'type': 'bool'
            },
            {
                'name': 'alert_offline',
                'type': 'bool'
            },
            {
                'name': 'alert_delta',
                'type': 'int'
            },
            {
                'name': 'port_scan',
                'type': 'bool'
            },
            {
                'name': 'last_port_scan',
                'type': 'datetime'
            },
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
        ]
        self.setup()

    def __repr__(self):
        if self.name:
            return "<Device %s>" % self.name
        return "<Device %s>" % self.mac

    def get_by_mac(self, mac: str):
        """
        Gets a device from the devices table based on mac address.

        """
        sql = """SELECT * FROM devices WHERE mac='%s'""" % mac
        self.cursor.execute(sql)
        device_raw = self.cursor.fetchone()
        if not device_raw:
            return self

        self.build_from_list(device_raw)

        return self

    def set_icon(self):
        """
        Attempts to set a device icon.

        """
        if self.icon:
            return

        if self.vendor == "Apple":
            self.icon = "fab fa-apple"

        if not self.name:
            self.icon = "fas fa-question"

# End File: lan-nanny/modules/models/device.py
