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

    def create_deaults(self):
        """
        """
        _create_default('timezone', 'America/Denver', 'str')
        _create_default('alert-new-device', '1', 'bool')
        _create_default('active-timeout', '8', 'int')
        _create_default('scan-hosts-enabled', '1', 'bool')
        _create_default('scan-hosts-ports', '0', 'bool')
        _create_default('scan-hosts-range', '192.168.50.1-255', 'str')
        _create_default('beta-features', 0, 'bool')

    def _create_default(option_name, option_value, option_type):
        option = Option(self.conn, self.cursor)
        option.get_by_name(option_name)
        if not option.name:
            option.name = option_name
            option.value = option_value
            option.type = option_type
        else:
            option.value = option_value
        option.save()



# End File: lan-nanny/modules/collections/options.py
