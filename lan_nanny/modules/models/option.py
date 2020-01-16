"""Option Model

"""
import logging

from .base import Base


class Option(Base):

    def __init__(self, conn=None, cursor=None):
        super(Option, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'options'
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
        return "<Option %s:%s>" % (self.name, self.value)

    def get_by_name(self, name: str=None) -> bool:
        """
        Gets an option from the options table based on name.

        """
        if not name:
            name = self.name
        if not name:
            raise ValueError('Missing name class var and method argument.')

        sql = """SELECT * FROM options WHERE name='%s'""" % name
        self.cursor.execute(sql)
        option_raw = self.cursor.fetchone()
        if not option_raw:
            return False

        self.build_from_list(option_raw)

        return True

    def build_from_list(self, raw: list):
        """
        Build a model from an ordered list, converting data types to their desired type where
        possible.

        """
        count = 0

        for field in self.total_map:
            setattr(self, field['name'], raw[count])
            count += 1

        if self.type == 'bool':
            self.value = self._set_bool(self.value)

        return True

    def update(self):
        """Save an option with Option types preserved."""
        if self.type == 'bool':
            if self.value == 'true':
                self.value = 1
            elif self.value == 'false':
                self.value = 0
        return self.save()


    def _set_bool(self, value) -> bool:
        """
        Sets a boolean option to the correct value.

        """
        value = str(value).lower()
        # Try to convert values to the positive.
        if value == '1' or value == 'true':
            return True
        # Try to convert values to the negative.
        elif value == '0' or value == 'false':
            return False


# End File: lan-nanny/lan_nanny/modules/models/option.py
