"""Options
Gets collections of options.

"""
from werkzeug.security import generate_password_hash

from ..models.option import Option
from .. import utils


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

    def set_defaults(self):
        """Tool for creating option defaults if they do not exist"""
        default_opts = [
            {
                'name': 'timezone',
                'type': 'str',
                'default': 'America/Denver'
            },
            {
                'name': 'alert-new-device',
                'type': 'bool',
                'default': True
            },
            {
                'name': 'active-timeout',
                'type': 'int',
                'default': 16
            },
            {
                'name': 'beta-features',
                'type': 'bool',
                'default': False
            },
            {
                'name': 'scan-hosts-enabled',
                'type': 'bool',
                'default': True
            },
            {
                'name': 'scan-hosts-range',
                'type': 'str',
            },
            {
                'name': 'scan-ports-enabled',
                'type': 'bool',
                'default': True,
            },
            {
                'name': 'scan-ports-default',
                'type': 'bool',
                'default': True
            },
            {
                'name': 'scan-ports-per-run',
                'type': 'int',
                'default': 2
            },
            {
                'name': 'scan-ports-interval',
                'type': 'int',
                'default': 2
            },
            {
                'name': 'console-password',
                'type': 'str',
            },
            {
                'name': 'db-prune-days',
                'type': 'int',
            },
        ]
        gen_pass = None
        for opt in default_opts:
            option = Option(self.conn, self.cursor)
            option.get_by_name(opt['name'])
            if option.name:
                continue

            if opt['name'] != 'console-password':
                option.set_default(opt)

            if opt['name'] == 'console-password':
                gen_pass = utils.make_default_password()
                opt['default'] = generate_password_hash(gen_pass, "sha256")
                option.set_default(opt)
        return gen_pass



# End File: lan-nanny/lan_nanny/modules/collections/options.py
