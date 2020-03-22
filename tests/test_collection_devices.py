"""Test Device Collections

"""
import os

import arrow

from lan_nanny.modules import db
from lan_nanny.modules.models.device import Device
from lan_nanny.modules.collections.devices import Devices

test_db = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-devices.db')
conn, cursor = db.create_connection(test_db)


class TestCollectionDevices:

    def test___init__(self):
        """Tests the Device.__init__ method."""
        device = Device(conn, cursor)
        device.setup()
        assert device.conn == conn
        assert device.cursor == cursor
        assert device.iodku
        assert device.table_name == 'devices'
        # assert device.total_map == DEVICE_TABLE_MAP

    def test_create_table(self):
        """Tests the Device.create_table method."""
        device = Device(conn, cursor)
        device.setup()
        assert device.create_table()

    def test_insert(self):
        """Tests the Device.insert method."""
        device = Device(conn, cursor)
        device.setup()
        device.mac = "38:D5:47:DC:48:18"
        device.vendor = "Asustek Computer"
        device.ip = "192.168.50.1"
        device.last_seen = arrow.utcnow().datetime
        device.first_seen = arrow.utcnow().datetime
        device.name = "Router"
        device.icon = "fas fa-wifi"
        device.port_scan = True
        device.last_port_scan_id = 1
        device.first_port_scan_id = 1
        device.port_scan_lock = False
        device.host_names = None
        device.insert()

        new_device = Device(conn, cursor)
        new_device.get_by_id(1)

        assert new_device.id == 1
        assert new_device.mac == device.mac
        assert new_device.vendor == device.vendor
        assert new_device.ip == device.ip
        # assert new_device.port_scan_lock == device.port_scan_lock

    def test_get_by_mac(self):
        """Tests the Device.get_by_mac method."""
        device = Device(conn, cursor)
        device.setup()
        device.get_by_mac("38:D5:47:DC:48:18")

        assert device.id == 1
        assert device.mac == "38:D5:47:DC:48:18"

    def test_set_icon(self):
        """Tests the Device.set_icon method."""
        device = Device(conn, cursor)
        device.setup()
        device.name = "My mac"
        device.vendor = "Apple"
        device.set_icon()
        assert device.icon == "fab fa-apple"

    def test_online(self):
        """Tests the Device.online method."""
        device = Device(conn, cursor)
        device.setup()
        device.name = "My mac"
        device.vendor = "Apple"
        assert not device.online()

    @classmethod
    def teardown_class(cls):
        """Tears down the sqlite database after tests finish."""
        os.remove(test_db)

# EndFile: lan-nanny/tests/test_model_device.py
