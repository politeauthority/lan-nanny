"""Test Device Model

"""
import os

import arrow

from lan_nanny.modules import db
from lan_nanny.modules.models.device import Device
from lan_nanny.modules.models.device_port import DevicePort
from lan_nanny.modules.models.entity_meta import EntityMeta

from .data import data_devices

test_db = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.db')
conn, cursor = db.create_connection(test_db)


class TestModelDevice:

    def test___init__(self):
        """Test the Base.__init__ method."""
        device = Device(conn, cursor)
        assert device.conn == conn
        assert device.cursor == cursor
        assert device.iodku
        assert device.table_name == 'devices'
        # assert device.field_map == DEVICE_TABLE_MAP

    def test_create_table(self):
        """Tests the Device tables creation, devices, device_ports and entity_metas"""
        device = Device(conn, cursor)
        assert device.create_table()

        device_port = DevicePort(conn, cursor)
        assert device_port.create_table()

        entity_meta = EntityMeta(conn, cursor)
        assert entity_meta.create_table()

    def test_insert(self):
        """Test the Device.insert method."""

        # Create all the test devices.
        for test_device in data_devices.devices:
            device = Device(conn, cursor)
            device.setup()
            device.mac = test_device['mac']
            device.vendor = test_device['vendor']
            device.ip = test_device['ip']
            device.last_seen = test_device['last_seen']
            device.first_seen = test_device['first_seen']
            device.name = test_device['name']
            device.hide = test_device['hide']
            device.favorite = test_device['favorite']
            device.icon = test_device['icon']
            device.port_scan = test_device['port_scan']
            device.last_port_scan = test_device['last_port_scan']
            device.last_port_scan_id = test_device['last_port_scan_id']
            device.first_port_scan_id = test_device['first_port_scan_id']
            device.port_scan_lock = test_device['port_scan_lock']
            device.host_names = test_device['host_names']
            device.type = test_device['type']
            assert device.insert()

        # Test that we retrieve the same data we expected to write.
        for test_device in data_devices.devices:
            new_device = Device(conn, cursor)
            assert new_device.get_by_mac(test_device['mac'])
            assert new_device.mac == test_device['mac']
            assert new_device.vendor == test_device['vendor']
            assert new_device.last_seen == test_device['last_seen']
            assert new_device.first_seen == test_device['first_seen']
            assert new_device.name == test_device['name']
            # assert new_device.hide == test_device['hide']
            assert new_device.favorite == test_device['favorite']
            assert new_device.icon == test_device['icon']
            # assert new_device.port_scan == test_device['port_scan']
            assert new_device.last_port_scan == test_device['last_port_scan']
            assert new_device.last_port_scan_id == test_device['last_port_scan_id']
            assert new_device.first_port_scan_id == test_device['first_port_scan_id']
            # assert new_device.port_scan_lock == test_device['port_scan_lock']
            assert new_device.host_names == test_device['host_names']
            assert new_device.type == test_device['type']

    def test_get_by_mac(self):
        """Test the Device.get_by_mac method."""
        for test_device in data_devices.devices:
            new_device = Device(conn, cursor)
            assert new_device.get_by_mac(test_device['mac'])


    def test_set_icon(self):
        """
           Test the device.set_icon method, to make sure it sets default device icons appropriately.
        """
        device = Device(conn, cursor)
        device.icon = "fab fa-icon-already-set"
        device.set_icon()
        assert device.icon == "fab fa-icon-already-set"

        device = Device(conn, cursor)
        device.vendor = "Apple"
        device.set_icon()
        # assert device.icon == "fab fa-apple"

        device = Device(conn, cursor)
        device.name = "9e:78:21:34:61:c6"
        device.mac = "9e:78:21:34:61:c6"
        device.set_icon()
        assert device.icon == "fas fa-question"

    @classmethod
    def teardown_class(cls):
        """Tears down the sqlite database after tests finish."""
        os.remove(test_db)


# EndFile: lan-nanny/tests/test_model_device.py
