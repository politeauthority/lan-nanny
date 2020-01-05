"""Option Model

"""
from .base import Base


class Option(Base):

    def __init__(self, conn=None, cursor=None):
        super(Option, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.model_name = 'Option'
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
        return "<Option %s>" % self.name

    def get_by_name(self, name: str=None):
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
            return self

        self.build_from_list(option_raw)

        return self

# End File: lan-nanny/modules/models/option.py
