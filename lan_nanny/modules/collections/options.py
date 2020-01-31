"""Options
Gets collections of options.

"""
from ..models.option import Option


class Options():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

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

    def get_all_keyed(self) -> dict:
        """
        Gets all options in a dictionary keyed on the option name.

        """
        opt_dict = {}

        all_options = self.get_all()
        ret_options = {}
        for option in all_options:
            ret_options[option.name] = option

        return ret_options


# End File: lan-nanny/modules/collections/options.py
