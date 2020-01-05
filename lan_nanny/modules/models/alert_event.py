"""Alert Event

"""
from .base import Base


class AlertEvent(Base):

    def __init__(self, conn=None, cursor=None):
        super(AlertEvent, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'AlertEvent'
        self.table_name = 'alert_events'
        self.field_map = [
            {
                'name': 'alert_id',
                'type': 'int',
            },
            {
                'name': 'event_type',
                'type': 'str'
            }
        ]
        self.setup()

# End File: lan-nanny/lan_nanny/modules/models/alert_event.py
