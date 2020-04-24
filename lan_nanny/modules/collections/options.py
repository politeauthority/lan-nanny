"""Options Collection
Gets collections of options.

"""
from werkzeug.security import generate_password_hash

from .base import Base
from ..models.option import Option
from .. import utils


class Options(Base):

    def __init__(self, conn=None, cursor=None):
        super(Options, self).__init__(conn, cursor)
        self.table_name = Option().table_name
        self.collect_model = Option

    def get_all_keyed(self) -> dict:
        """Get all options in a dictionary keyed on the option name."""
        all_options = self.get_all()
        ret_options = {}
        for option in all_options:
            ret_options[option.name] = option
        return ret_options

    def set_defaults(self):
        """Tool for creating option defaults if they do not exist."""
        default_opts = [
            {
                'name': 'timezone',
                'type': 'str',
                'default': 'America/Denver'
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
                'name': 'console-password-enabled',
                'type': 'bool',
                'default': False
            },
            {
                'name': 'console-password',
                'type': 'str',
            },
            {
                'name': 'api-enabled',
                'type': 'bool',
                'default': False
            },
            {
                'name': 'api-key',
                'type': 'str',
            },
            {
                'name': 'db-prune-days',
                'type': 'int',
            },
            {
                'name': 'auto-reload-console',
                'type': 'bool',
                'default': True
            },
            {
                'name': 'system-name',
                'type': 'str',
            },
            {
                'name': 'alerts-enabled',
                'type': 'bool',
                'default': False,
            },
            {
                'name': 'alerts-new-device',
                'type': 'bool',
                'default': True
            },
            {
                'name': 'console-ui-color',
                'type': 'str',
                'default': 'black'
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
