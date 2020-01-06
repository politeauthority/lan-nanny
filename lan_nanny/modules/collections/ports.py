"""Ports
Gets collections of ports.

"""
from ..models.port import Port


class Ports():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_distinct(self) -> list:
        """
        Gets all ports by a device_id.

        """
        sql = """
            SELECT DISTINCT *
            FROM ports
            """

        self.cursor.execute(sql)
        ports_raw = self.cursor.fetchall()
        ports = []
        for raw_port in ports_raw:
            port = Port(self.conn, self.cursor)
            port.build_from_list(raw_port)
            ports.append(port)

        return ports


    def get_by_device(self, device_id: int) -> list:
        """
        Gets all ports by a device_id.

        """
        sql = """
            SELECT *
            FROM ports
            WHERE device_id = %s """ % device_id

        self.cursor.execute(sql)

        ports_raw = self.cursor.fetchall()

        ports = []
        for raw_port in ports_raw:
            port = Port(self.conn, self.cursor)
            port.build_from_list(raw_port)
            ports.append(port)

        return ports

# End File: lan-nanny/modules/collections/ports.py
