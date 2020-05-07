"""Config Help

"""
from importlib import import_module
import os 


def get_config():
    """Get the application configs."""
    if os.environ.get('LAN_NANNY_CONFIG'):
        config_file = os.environ.get('LAN_NANNY_CONFIG')
        configs = import_module('config.%s' % config_file)
        # imported_module = import_module('.config.%s' % config)
        print('Using config: %s' % os.environ.get('LAN_NANNY_CONFIG') )
    else:
        print('Using config: default')
        configs = import_module('config.default')
    return configs

# End File: lan-nanny/lan_nanny/modules/config_help.py