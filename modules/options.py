"""Options
Gets collections of options.

"""
from .option import Option


class Options():

    def __init__(self):
        self.conn = None
        self.cursor = None

    def get_all(self):
        """
        Gets all devices in the database.

        """
        sql = """
            SELECT *
            FROM options
            """

        self.cursor.execute(sql)
        raw_options = self.cursor.fetchall()
        options = []
        for raw_option in raw_options:
            option = Option()
            option.build_from_list(raw_option)
            options.append(option)
        return options

# End File: lan-nanny/modules/options.py
