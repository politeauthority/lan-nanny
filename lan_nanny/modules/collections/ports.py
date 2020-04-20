"""Ports
Gets collections of ports.

"""
from .base import Base
from .. import utils
from ..models.port import Port


class Ports(Base):

    def __init__(self, conn=None, cursor=None):
        super(Ports, self).__init__(conn, cursor)
        self.collect_model = Port
        self.table_name = self.collect_model().table_name

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
        ports = self.self.build_from_lists(raw_ports)
        return ports

    def get_privileged(self):
        """Collect ports that a privileged, ie running on 1000 or under."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                number <= 1000;""" % (self.table_name)
        self.cursor.execute(sql)
        raw_ports = self.cursor.fetchall()
        ports = self.build_from_lists(raw_ports)
        return ports

# End File: lan-nanny/modules/collections/ports.py
