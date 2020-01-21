"""Ports
Gets collections of ports.

"""
from ..models.port import Port
from .. import utils


class Ports:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_distinct(self) -> list:
        """Get all ports by a device_id."""
        sql = """
            SELECT DISTINCT(port)
            FROM ports
            """

        self.cursor.execute(sql)
        distinct_ports_raw = self.cursor.fetchall()

        ports = []
        for distinct_port in distinct_ports_raw:
            port = Port(self.conn, self.cursor)
            port.get_by_port_number(distinct_port)
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

    def search(self, phrase):
        """Collect ports matching a search phrase, matching the port number or service name."""
        port_sql = utils.gen_like_sql('port', phrase)
        service_name_sql = utils.gen_like_sql('service_name', phrase)
        sql = """
            SELECT *
            FROM ports
            WHERE
            %(port)s OR
            %(service_name)s """ % {
            'port': port_sql,
            'service_name': service_name_sql}
        self.cursor.execute(sql)
        raw_ports = self.cursor.fetchall()
        ports = []
        for raw_port in raw_ports:
            port = Port(self.conn, self.cursor)
            port.build_from_list(raw_port)
            ports.append(port)
        return ports

    def delete_device(self, device_id: int) -> list:
        """Delete all ports containing a device."""
        sql = """
            DELETE FROM ports
            WHERE device_id = %s """ % device_id

        self.cursor.execute(sql)
        self.conn.commit()

        return True

# End File: lan-nanny/modules/collections/ports.py
