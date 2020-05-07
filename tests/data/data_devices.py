"""Data Devices

"""
from datetime import timedelta
import pprint

from faker import Faker
from faker.providers import internet

from lan_nanny.modules.models.device import Device

import arrow



fake = Faker()
fake.add_provider(internet)
now = arrow.utcnow().datetime


devices = [
    {
        "mac": fake.mac_address(),
        "vendor": "Asustek Computer",
        "ip": "192.168.50.1",
        "last_seen": now,
        "first_seen": now,
        "name": "Router",
        "hide": False,
        "favorite": True,
        "icon": "fas fa-wifi",
        "port_scan": True,
        "last_port_scan": now,
        "last_port_scan_id": 1,
        "first_port_scan_id": 1,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Router",
        "ports": [{
            'device_id': None,  # Must be set at runtime
            'port_id': None,    # Must be set at runtime
            'last_seen': now,
            'state': 'open',
            'updated_ts': now
        }
        ]
    },
    {
        "mac": fake.mac_address(),
        "vendor": "Apple",
        "ip": "192.168.50.232",
        "last_seen": now,
        "first_seen": now,
        "name": "Bill's Laptop",
        "hide": False,
        "favorite": False,
        "icon": "fas fa-laptop",
        "port_scan": False,
        "last_port_scan": now,
        "last_port_scan_id": None,
        "first_port_scan_id": None,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Laptop"
    },
    {
        "mac": fake.mac_address(),
        "vendor": "Apple",
        "ip": "192.168.50.200",
        "last_seen": now,
        "first_seen": now,
        "name": "Bill's iPhone",
        "hide": False,
        "favorite": True,
        "icon": "fas fa-mobile",
        "port_scan": True,
        "last_port_scan": now,
        "last_port_scan_id": 2,
        "first_port_scan_id": 2,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Smart Phone"
    },
    {
        "mac": fake.mac_address(),
        "vendor": "Apple",
        "ip": "192.168.50.192",
        "last_seen": now - timedelta(days=2),
        "first_seen": now - timedelta(days=5),
        "name": "Amy's iPhone",
        "hide": False,
        "favorite": True,
        "icon": "fas fa-mobile",
        "port_scan": True,
        "last_port_scan": now - timedelta(days=3),
        "last_port_scan_id": 2,
        "first_port_scan_id": 2,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Smart Phone"
    },
    {
        "mac": fake.mac_address(),
        "vendor": "Raspberry Pi",
        "ip": "192.168.50.4",
        "last_seen": now - timedelta(hours=5),
        "first_seen": now - timedelta(days=10),
        "name": "Raspberry Pi",
        "hide": False,
        "favorite": False,
        "icon": "fas fa-rasppberry-pi",
        "port_scan": True,
        "last_port_scan": now - timedelta(days=3),
        "last_port_scan_id": 2,
        "first_port_scan_id": 2,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Raspberry Pi"
    }

]


def create_devices(conn, cursor):
    """Create the test devices. """
    for test_device in devices:
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
    return True

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(devices)
    print(fake.mac_address())


# End File: lan-nanny/tests/data/data_devices.py