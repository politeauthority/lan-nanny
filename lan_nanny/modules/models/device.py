"""Device Model

"""
import logging

import arrow

from flask import g

from .base import Base
from ..collections.ports import Ports


class Device(Base):
    """Device object, representing a LanNanny registered device."""

    def __init__(self, conn=None, cursor=None):
        """Device init for a new device object, passing SQLite connection parameters."""
        super(Device, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
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
                'type': 'bool',
                'default': 0,
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
                'name': 'flagged_for_scan',
                'type': 'bool',
                'default': '0'
            },
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
        ]
        self.ports = []
        self.setup()

    def __repr__(self):
        """Device representationm show the name if we have one."""
        return "<Device %s>" % self.name

    def get_by_mac(self, mac: str):
        """Get a device from the devices table based on mac address."""
        sql = """SELECT * FROM devices WHERE mac='%s'""" % mac
        self.cursor.execute(sql)
        device_raw = self.cursor.fetchone()
        if not device_raw:
            return self

        self.build_from_list(device_raw)

        return self

    def set_icon(self):
        """Attempt to set a device icon."""
        if self.icon:
            return

        if self.vendor == "Apple":
            self.icon = "fab fa-apple"

        if self.name == self.mac:
            self.icon = "fas fa-question"

    def online(self) -> bool:
        """Determine if a device is considered 'online' currently."""
        if not self.last_seen:
            return False
        online_delta = arrow.utcnow().datetime - self.last_seen
        if online_delta < timedelta(minutes=g.options['active-timeout'].value):
            return True
        return False

    def build_from_list(self, raw: list, build_ports: bool=False):
        """
        Build a model from an ordered list, converting data types to their desired type where
        possible.

        """
        super(Device, self).build_from_list(raw)
        if build_ports:
            self.check_required_class_vars()
            ports = Ports(self.conn, self.cursor)
            self.ports = ports.get_by_device(self.id)
        return True

# End File: lan-nanny/modules/models/device.py
