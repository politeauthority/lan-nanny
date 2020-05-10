"""Alert - Model
Alert model extends BaseEntityMeta allowing the object to have meta objects.

"""
from .base_entity_meta import BaseEntityMeta
from .device import Device


class Alert(BaseEntityMeta):

    def __init__(self, conn=None, cursor=None):
        super(Alert, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'alerts'
        self.field_map = [
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
            {
                'name': 'last_observed_ts',
                'type': 'datetime'
            },
            {
                'name': 'resolved_ts',
                'type': 'datetime'
            },
            {
                'name': 'kind',
                'type': 'str'
            },
            {
                'name': 'notification_sent',
                'type': 'int'
            },
            {
                'name': 'acked',
                'type': 'bool',
                'default': False,
            },
            {
                'name': 'acked_ts',
                'type': 'datetime'
            },
            {
                'name': 'active',
                'type': 'bool',
                'default': True,
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
            return "<Alert %s:%s>" % (self.kind, self.id)
        return "<Alert>"

    def delete_device(self, device_id: int) -> bool:
        """Deletes all records from the `alerts` table containing a device_id, this should be
           performed when deleting a device.
        """
        sql = """DELETE FROM alerts WHERE device_id = %s """ % device_id
        self.cursor.execute(sql)
        return True

# End File: lan-nanny/lan_nanny/modules/models/alert.py
