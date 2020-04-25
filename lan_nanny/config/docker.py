"""Docker configs

"""
import os

DEBUG = True

APP_PORT = 5000
LAN_NANNY_DB_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../../'
    'galapago.db')

LAN_NANNY_TMP_DIR = "/tmp"


# End File: lan-nanny/lan_nanny/config/docker.py
