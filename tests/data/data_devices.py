"""Data Devices

"""
import pprint

from faker import Faker
from faker.providers import internet

import arrow



fake = Faker()
fake.add_provider(internet)


devices = [
    {
        "mac": fake.mac_address(),
        "vendor": "Asustek Computer",
        "ip": "192.168.50.1",
        "last_seen": arrow.utcnow().datetime,
        "first_seen": arrow.utcnow().datetime,
        "name": "Router",
        "hide": False,
        "favorite": True,
        "icon": "fas fa-wifi",
        "port_scan": True,
        "last_port_scan": arrow.utcnow().datetime,
        "last_port_scan_id": 1,
        "first_port_scan_id": 1,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Router",
        "ports": [{
            'device_id': None,  # Must be set at runtime
            'port_id': None,    # Must be set at runtime
            'last_seen': arrow.utcnow().datetime,
            'state': 'open',
            'updated_ts': arrow.utcnow().datetime
        }
        ]
    },
    {
        "mac": fake.mac_address(),
        "vendor": "Apple",
        "ip": "192.168.50.232",
        "last_seen": arrow.utcnow().datetime,
        "first_seen": arrow.utcnow().datetime,
        "name": "Bill's Laptop",
        "hide": False,
        "favorite": False,
        "icon": "fas fa-laptop",
        "port_scan": False,
        "last_port_scan": arrow.utcnow().datetime,
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
        "last_seen": arrow.utcnow().datetime,
        "first_seen": arrow.utcnow().datetime,
        "name": "Bill's iPhone",
        "hide": False,
        "favorite": True,
        "icon": "fas fa-mobile",
        "port_scan": True,
        "last_port_scan": arrow.utcnow().datetime,
        "last_port_scan_id": 2,
        "first_port_scan_id": 2,
        "port_scan_lock": False,
        "host_names": None,
        "type": "Smart Phone"
    }
]

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(devices)
    print(fake.mac_address())


# End File: lan-nanny/tests/data/data_devices.py