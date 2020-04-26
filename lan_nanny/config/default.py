"""Default configs

"""
import os

DEBUG = False

APP_PORT = 5000
LAN_NANNY_DB_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../../'
    'galapago.db')

LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'pass': 'password',
    'port': 3306,
    'name': 'lan_nanny'
}


# End File: lan-nanny/lan_nanny/config/default.py
