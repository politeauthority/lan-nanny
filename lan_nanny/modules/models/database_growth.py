"""Database Growth Model

"""
from datetime import datetime, timedelta

import arrow

from .base import Base


class DatabaseGrowth(Base):

    def __init__(self, conn=None, cursor=None):
        super(DatabaseGrowth, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'database_growth'
        self.field_map = [
            {
                'name': 'size',
                'type': 'int',
            },
        ]
        self.setup()

    def get_24_hours_ago(self):
        """Get 24 hours ago."""
        date_24_hours_ago = arrow.utcnow().datetime - timedelta(hours=24)
        sql = """
            SELECT *
            FROM %s
            WHERE created_ts>='%s'
            ORDER BY created_ts
            LIMIT 1;
        """ % (self.table_name, str(date_24_hours_ago))
        self.cursor.execute(sql)
        raw_db_growth = self.cursor.fetchone()
        if not raw_db_growth:
            return False
        self.build_from_list(raw_db_growth)
        return True

    def get_hours_ago(self, hours: int):
        """Get x hours ago."""
        date_hours_ago = arrow.utcnow().datetime - timedelta(hours=hours)
        sql = """
            SELECT *
            FROM %s
            WHERE created_ts>='%s'
            ORDER BY created_ts
            LIMIT 1;
        """ % (self.table_name, str(date_24_hours_ago)[0:10])
        self.cursor.execute(sql)
        raw_db_growth = self.cursor.fetchone()
        if not raw_db_growth:
            return False
        self.build_from_list(raw_db_growth)
        return True


# End File: lan-nanny/lan_nanny/modules/models/database_growth.py
