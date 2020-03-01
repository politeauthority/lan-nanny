"""Sys Info Model

"""
import logging

from .base import Base


class SysInfo(Base):

    def __init__(self, conn=None, cursor=None):
        super(SysInfo, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'sys_infos'
        self.field_map = [
            {
                'name': 'name',
                'type': 'str',
            },
            {
                'name': 'type',
                'type': 'str'
            },
            {
                'name': 'value',
                'type': 'str'
            },
            {
                'name': 'update_ts',
                'type': 'datetime'
            }
        ]
        self.setup()

    def __repr__(self):
        return "<SysInfo %s:%s>" % (self.name, self.value)

# End File: lan-nanny/lan_nanny/modules/models/sys_info.py
