"""Default configs

"""
import os

DEBUG = False

APP_PORT = 5000
LAN_NANNY_DB_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../../'
    'galapago.db')

# End File: lan-nanny/lan_nanny/config/default.py
