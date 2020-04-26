"""Docker configs

"""
import os

DEBUG = True

APP_PORT = 5000
LAN_NANNY_DB_FILE = None
LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_DB = {
    'host': os.environ.get('LAN_NANNY_DB_HOST'),
    'user': os.environ.get('LAN_NANNY_DB_USER'),
    'pass': os.environ.get('LAN_NANNY_DB_PASS'),
    'port': int(os.environ.get('LAN_NANNY_DB_PORT', 3306)),
    'name': os.environ.get('LAN_NANNY_DB_NAME'),
}



# End File: lan-nanny/lan_nanny/config/docker.py
