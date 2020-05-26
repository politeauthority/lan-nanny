"""Notifications - Model

"""
from .base_entity_meta import BaseEntityMeta


class Notification(BaseEntityMeta):

    def __init__(self, conn=None, cursor=None):
        super(Notification, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'notifications'
        self.field_map = [
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
            {
                'name': 'alerts_contained',
                'type': 'int'
            },
            {
                'name': 'delivered',
                'type': 'bool'
                'default': False,
            },
            {
                'name': 'message',
                'type': 'str'
            },
        ]
        self.metas = {}
        self.setup()

    def __repr__(self):
        if self.kind:
            return "<Notification %s:%s>" % (self.kind, self.id)
        return "<Notification>"


# End File: lan-nanny/lan_nanny/modules/models/notification.py
