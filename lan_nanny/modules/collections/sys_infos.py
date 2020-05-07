"""Sys Infos
Gets collections of sys infos.

"""
from .base import Base
from ..models.sys_info import SysInfo

class SysInfos(Base):

    def __init__(self, conn=None, cursor=None):
        super(SysInfos, self).__init__(conn, cursor)
        self.table_name = SysInfo().table_name
        self.collect_model = SysInfo

# End File: lan-nanny/lan_nanny/modules/collections/sys_infos.py
