"""Device Model

"""
from datetime import timedelta
import logging

import arrow

from flask import g

from .base_entity_meta import BaseEntityMeta
from .device_mac import DeviceMac
from ..collections.device_macs import DeviceMacs
from ..collections.device_ports import DevicePorts


class Device(BaseEntityMeta):
    """Device object, representing a LanNanny registered device."""

    def __init__(self, conn=None, cursor=None):
        """Device init for a new device object, passing SQLite connection parameters. """
        super(Device, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = 'devices'

        self.field_map = [
            {
                'name': 'update_ts',
                'type': 'datetime'
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
                'name': 'port_scan',
                'type': 'bool'
            },
            {
                'name': 'last_port_scan',
                'type': 'datetime'
            },
            {
                'name': 'last_port_scan_id',
                'type': 'int',
            },
            {
                'name': 'first_port_scan_id',
                'type': 'int',
            },
            {
                'name': 'port_scan_lock',
                'type': 'bool',
            },
            {
                'name': 'host_names',
                'type': 'str',
            },
            {
                'name': 'kind',
                'type': 'str',
                'default': 'Unknown',
            },
        ]
        self.ports = []
        self.macs = []
        self.metas = {}

        self.setup()

    def __repr__(self):
        """Device representation show the name if we have one."""
        return "<Device: %s>" % self.name

    def get_by_mac(self, mac: str) -> bool:
        """Get a device from the devices table based on mac address."""
        sql = """
            SELECT *
            FROM device_macs
            WHERE mac_addr='%s'; """ % mac
        self.cursor.execute(sql)
        device_mac_raw = self.cursor.fetchone()
        if not device_mac_raw:
            return False

        self.get_by_id(device_mac_raw[3])

        return True

    def get_ports(self):
        """Get device ports added to self.ports."""
        device_ports = DevicePorts(self.conn, self.cursor)
        self.ports = device_ports.get_by_device_id(self.id)
        return True

    def get_macs(self):
        """Get device macs added to self.macs. """
        device_macs = DeviceMacs(self.conn, self.cursor)
        self.macs = device_macs.get_by_device_id(self.id)
        return True

    def get_alert_jitter(self):
        """Get the Device's alert jitter meta setting if it exists, or return None. """
        if 'alert_jitter' not in self.metas:
            return None
        jitter = self.metas['alert_jitter']
        if jitter.value.isdigit():
            return int(jitter.value)
        return None

    def set_icon(self):
        """Attempt to set a device icon."""
        if self.icon:
            return

        if self.vendor == "Apple":
            self.icon = "fab fa-apple"

        if self.name == self.mac:
            self.icon = "fas fa-question"

    def set_vendor(self, vendor: str) -> bool:
        """Set the vendor value for a device, if the vendor is a suitable name, update that as
           well.
        """
        if not vendor:
            return True
        self.vendor = vendor

        # If the device doesn't have a name, or it's name is set to its mac as a placeholder, update
        # it to it's vendor
        if not self.name or (self.name == self.mac):
            self.name = self.vendor
        return True

    def online(self) -> bool:
        """Determine if a device is considered 'online' currently."""
        if not self.last_seen:
            return False
        online_delta = arrow.utcnow().datetime - self.last_seen
        if online_delta < timedelta(minutes=int(g.options['active-timeout'].value)):
            return True
        return False

    def build_from_list(self, raw: list, meta: bool = False, build_ports: bool = False):
        """Build a model from an ordered list, converting data types to their desired type where
           possible.
        """
        super(Device, self).build_from_list(raw, meta=meta)
        self.get_macs()
        if build_ports:
            self.get_ports()
        return True

    def insert(self):
        """Insert a new record of the model.
           @unit-tested
        """
        super(Device, self).insert()
        try:
            getattr(self, 'scan_mac_info')
            self._create_new_device_mac(self.scan_mac_info)
        except AttributeError:
            logging.debug('Device is not coming from scan.')
            logging.debug('Device is not coming from scan.')
            logging.debug('Device is not coming from scan.')

        return True

    def unpack(self):
        """Unpack a serial model object into a flat dictionary of  the model's keys and values. Also
           grabbing device macs.
        """
        unpack = super(Device, self).unpack()
        self.get_macs()
        unpack['macs'] = []
        for mac in self.macs:
            unpack['macs'].append(mac.mac_addr)
        return unpack

    def _create_new_device_mac(self, scan_mac_info: {}) -> bool:
        """Create a new device-mac pairing, with a given mac address. """
        now = arrow.utcnow().datetime
        device_mac = DeviceMac(self.conn, self.cursor)
        device_mac.device_id = self.id
        device_mac.mac_addr = scan_mac_info['mac']
        device_mac.ip_addr = scan_mac_info['ip']
        device_mac.last_seen = now
        device_mac.updated_ts = now
        device_mac.save()
        return True

# End File: lan-nanny/lan_nanny/modules/models/device.py
