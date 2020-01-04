"""Alert Events Collection
Gets collections of AlertEvents.

"""
from ..models.alert_event import AlertEvent


class AlertEvents():

    def __init__(self, conn=None, cursor=None) -> list:
        self.conn = conn
        self.cursor = cursor

    def get_by_alert_id(self, alert_id: int):
        sql = """
            SELECT *
            FROM alert_events
            WHERE alert_id = %s
            ORDER BY created_ts DESC;""" % alert_id

        self.cursor.execute(sql)
        raw_alert_events = self.cursor.fetchall()
        alert_events = []
        for raw_event_alert in raw_alert_events:
            event_alert = AlertEvent(self.conn, self.cursor)
            event_alert.build_from_list(raw_alert, build_device=True)
            event_alert.append(alert)
        return alert_events

# End File: lan-nanny/lan_nanny/modules/collections/alert_events.py
