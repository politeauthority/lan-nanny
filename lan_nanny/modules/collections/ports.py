"""Ports
Gets collections of ports.

"""
from ..models.port import Port
from .. import utils


class Ports:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_all(self) -> list:
        """Get all ports."""
        sql = """
            SELECT *
            FROM ports;
            """
        self.cursor.execute(sql)
        raw_ports = self.cursor.fetchall()

        ports = []
        for raw_port in raw_ports:
            port = Port()
            port.build_from_list(raw_port)
            ports.append(port)
        return ports

    def get_by_port_ids(self, port_ids: list) -> list:
        """Get ports by a list of port IDs."""
        port_ids_sql = ""
        for port_id in port_ids:
            port_ids_sql += "%s," % port_id
        port_ids_sql = port_ids_sql[:-1]
        sql = """
            SELECT *
            FROM ports
            WHERE id IN(%s);""" % (port_ids_sql)
        self.cursor.execute(sql)
        raw_ports = self.cursor.fetchall()
        ports = self._build_raw_ports(raw_ports)
        return ports

    def search(self, phrase):
        """Collect ports matching a search phrase, matching the port number or service name."""
        port_sql = utils.gen_like_sql('port', phrase)
        service_sql = utils.gen_like_sql('service', phrase)
        sql = """
            SELECT *
            FROM ports
            WHERE
            %(port)s OR
            %(service)s """ % {
            'port': port_sql,
            'service': service_sql}
        self.cursor.execute(sql)
        raw_ports = self.cursor.fetchall()
        ports = []
        for raw_port in raw_ports:
            port = Port(self.conn, self.cursor)
            port.build_from_list(raw_port)
            ports.append(port)
        return ports

    def _build_raw_ports(self, raw_ports) -> list:
        """Build raw ports into a list of fully built port objects."""
        ports = []
        for raw_port in raw_ports:
            port = Port()
            port.build_from_list(raw_port)
            ports.append(port)
        return ports

# End File: lan-nanny/modules/collections/ports.py
