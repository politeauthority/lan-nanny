"""Options Collection
Gets collections of options.

"""
import logging

# from werkzeug.security import generate_password_hash

from .base import Base
from ..models.option import Option
# from .. import utils


class Options(Base):

    def __init__(self, conn=None, cursor=None):
        super(Options, self).__init__(conn, cursor)
        self.table_name = Option().table_name
        self.collect_model = Option
        self.default_opts = [
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
                'name': 'debug-features',
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
                'default': '192.168.1.0/23'
            },
            {
                'name': 'scan-hosts-tool',
                'type': 'str',
                'default': 'arp'
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
                'default': 1
            },
            {
                'name': 'scan-ports-interval',
                'type': 'int',
                'default': 120
            },
            {
                'name': 'port-open-timeout',
                'type': 'int',
                'default': 84
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
                'name': 'db-prune-enabled',
                'type': 'bool',
                'default': False
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
            {
                'name': 'notification-slack-enabled',
                'type': 'bool',
                'default': False
            },
            {
                'name': 'notification-slack-token',
                'type': 'str',
                'default': '',
            },
            {
                'name': 'notification-slack-channel',
                'type': 'str',
                'default': '',
            },
        ]

    def set_defaults(self) -> bool:
        """Create Option values and set Option defaults where applicable. """
        print('Setting defaults')
        for opt in self.default_opts:
            logging.info('Option: %s' % opt['name'])
            option = Option(self.conn, self.cursor)
            option_made = option.set_default(opt)
            if option_made:
                logging.info('Created option: %s with value "%s"' % (option.name, option.value))
            else:
                logging.info('Not creating option: %s, already exists' % option.name)

        return True

    # Removing this function because password setup needs to be revisited.
    # def set_default_password(self):
    #     gen_pass = False
    #     for opt in self.default_opts:
    #         if opt['name'] != 'console-password':
    #             continue
    #         gen_pass = utils.make_default_password()
    #         opt['default'] = generate_password_hash(gen_pass, "sha256")
    #         new_pass = option.set_default(opt)
    #         if new_pass:
    #             gen_pass = new_pass
    #     return gen_pass


# End File: lan-nanny/lan_nanny/modules/collections/options.py
