"""Test Device Collections

"""
from datetime import timedelta
import os

import arrow

from lan_nanny.modules import db
from lan_nanny.modules.models.device import Device
from lan_nanny.modules.models.device_port import DevicePort
from lan_nanny.modules.models.entity_meta import EntityMeta
from lan_nanny.modules.collections.devices import Devices

from .configs import CONFIGS
from .data import data_devices

test_db = os.path.join(CONFIGS['tmp_dir'], 'test.db')
if os.path.exists(test_db):
    os.remove(test_db)
conn, cursor = db.create_connection(test_db)


class TestCollectionDevices:

    def test___init__(self):
        """Test the Devices.__init__ method."""
        devices = Devices(conn, cursor)
        assert devices.conn == conn
        assert devices.cursor == cursor
        assert devices.table_name
        assert devices.collect_model

    def test_create_table(self):
        """Test the Device.create_table method and insert test data."""
        device = Device(conn, cursor)
        assert device.create_table()

        device_port = DevicePort(conn, cursor)
        assert device_port.create_table()

        entity_meta = EntityMeta(conn, cursor)
        assert entity_meta.create_table()

        data_devices.create_devices(conn, cursor)

    def test_get_recent(self):
        """Test Devices.get_recent()"""
        devices = Devices(conn, cursor)
        recent_devices = devices.get_recent()
        assert isinstance(recent_devices, list)
        for device in recent_devices:
            assert device.last_seen

    def test_get_favorites(self):
        """Test Devices.get_favorites()"""
        devices = Devices(conn, cursor)
        favorite_devices = devices.get_favorites()
        assert isinstance(favorite_devices, list)
        for device in favorite_devices:
            assert device.favorite

    def test_get_new_count(self):
        """Test Devices.get_new_count()"""
        devices = Devices(conn, cursor)
        new_device_count = devices.get_new_count()
        assert isinstance(new_device_count, int)

    def test_get_new(self):
        """Test Devices.get_new()"""
        day_ago = arrow.utcnow().datetime - timedelta(hours=24)
        devices = Devices(conn, cursor)
        new_devices = devices.get_new()
        assert isinstance(new_devices, list)
        for device in new_devices:
            assert device.first_seen >= day_ago

    def test_with_enabled_port_scanning(self):
        """Test Devices.with_enabled_port_scanning()"""
        devices = Devices(conn, cursor)
        port_scan_devices = devices.with_enabled_port_scanning()
        assert isinstance(port_scan_devices, list)
        for device in port_scan_devices:
            assert device.port_scan

    def test_search(self):
        """Test Devices.search()"""
        devices = Devices(conn, cursor)

        # # Test searching a device name
        # devices_search_name = devices.search("Amy")
        # assert isinstance(devices_search_name, list)
        # test_validated = False
        # for device in devices_search_name:
        #     print(device.name)
        #     if device.name == "Amy's iPhone":
        #         test_validated = True
        #         break
        # assert test_validated

        # Test searching a vendor name
        # devices_search_vendor = devices.search('Apple')
        # assert isinstance(devices_search_vendor, list)
        # test_validated = False
        # for device in devices_search_vendor:
        #     if device.vendor == 'Apple':
        #         test_validated = True
        #         break
        # assert test_validated

    @classmethod
    def teardown_class(cls):
        """Tears down the sqlite database after tests finish."""
        if os.path.exists(test_db):
            os.remove(test_db)



# EndFile: lan-nanny/tests/test_model_device.py
