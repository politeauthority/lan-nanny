"""Option

"""
import arrow

class Option():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

        self.id = None
        self.name = None
        self.value = None
        self.update_ts = None

    def __repr__(self):
        return "<Option %s>" % self.name

    def get_by_name(self, name: str):
        """
        Gets an option from the options table based on name.

        """
        sql = """SELECT * FROM options WHERE name='%s'""" % name
        self.cursor.execute(sql)
        option_raw = self.cursor.fetchone()
        if not option_raw:
            return self
        
        self.build_from_list(option_raw)

        return self

    def create(self):
        """
        Creates an option from class vars.

        """
        now = arrow.utcnow().datetime
        sql = """
            INSERT INTO options
            (name, value, update_ts)
            VALUES (?, ?, ?)"""

        option = (
            self.name,
            self.value,
            now)

        self.cursor.execute(sql, option)
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return self

    def update(self) -> bool:
        """
        Updates an option in the `options` table setting its new value and update ts.

        """
        now = arrow.utcnow().datetime
        sql = """
            UPDATE options
            SET
                value = ?,
                update_ts = ?
            WHERE name = ?"""
        the_update = (
            self.value,
            now,
            self.name)
        self.cursor.execute(sql, the_update)
        self.conn.commit()

        return True

    def build_from_list(self, raw: list):
        """
        Creates a option from a raw row record.

        """
        self.id = raw[0]
        self.name = raw[1]
        self.value = raw[2]
        self.update_ts =  raw[3]


# End File: lan-nanny/modules/models/option.py
