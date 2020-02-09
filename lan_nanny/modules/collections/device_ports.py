"""Device Ports Collection.
Gets collections of device ports.

"""
from .base import Base
from ..models.device_port import DevicePort
from .ports import Ports


class DevicePorts(Base):
    """Collection class for gathering groups of device ports."""

    def __init__(self, conn=None, cursor=None):
        """ Store Sqlite conn and model table_name as well as the model obj for the collections
            target model.
        """
        super(DevicePorts, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = DevicePort().table_name
        self.collect_model = DevicePort

    def get_by_device_id(self, device_id) -> list:
        """Get all devices in the database."""
        sql = """
            SELECT *
            FROM device_ports
            WHERE device_id=%s
            ORDER BY last_seen DESC;""" % device_id
        self.cursor.execute(sql)
        raw_device_ports = self.cursor.fetchall()
        port_ids = []
        device_ports = []
        for raw_device_port in raw_device_ports:
            device_port = DevicePort()
            device_port.build_from_list(raw_device_port)
            port_ids.append(device_port.port_id)
            device_ports.append(device_port)
        ports = Ports(self.conn, self.cursor).get_by_port_ids(port_ids)

        for device_port in device_ports:
            for port in ports:
                if device_port.port_id == port.id:
                    device_port.port = port
                    break

        return device_ports

# End File: lan-nanny/lan_nanny/modules/collections/device_ports.py
