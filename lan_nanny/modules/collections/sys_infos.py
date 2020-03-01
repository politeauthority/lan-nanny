"""Sys Infos
Gets collections of sys infos.

"""
from .base import Base
from ..models.sys_info import SysInfo

class SysInfos(Base):

    def __init__(self, conn=None, cursor=None):
        super(SysInfos, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = SysInfo().table_name
        self.collect_model = SysInfo

    def get_all_keyed(self) -> dict:
        """Get all infos in a dictionary keyed on the info name."""
        all_infos = self.get_all()
        ret_infos = {}
        for info in all_infos:
            ret_infos[info.name] = info
        return ret_infos

# End File: lan-nanny/lan_nanny/modules/collections/sys_infos.py
