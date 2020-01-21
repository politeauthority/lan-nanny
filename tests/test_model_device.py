"""Test Device Model

"""
import os


from lan_nanny.modules import db
from lan_nanny.modules.models.device import Device

test_db = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.db')
conn, cursor = db.create_connection(test_db)
BASE_TABLE_MAP = [
    {
        'name': 'id',
        'type': 'int',
        'primary': True,
    },
    {
        'name': 'created_ts',
        'type': 'datetime',
    }
]
DEVICE_TABLE_MAP = [
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


class TestModelDevice:

    def test___init__(self):
        """
        Tests the Base.__init__ method.

        """
        device = Device(conn, cursor)
        assert device.conn == conn
        assert device.cursor == cursor
        assert device.iodku
        assert device.table_name == 'devices'
        # assert device.field_map == DEVICE_TABLE_MAP


# EndFile: lan-nanny/tests/test_model_device.py
