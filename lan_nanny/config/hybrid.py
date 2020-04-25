"""Hybrid configs

"""
import os

DEBUG = True

APP_PORT = 5050
LAN_NANNY_DB_FILE = None
LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_DB = {
    'host': '127.0.0.1',
    'user': 'user',
    'pass': 'password',
    'port': int(os.environ.get('LAN_NANNY_DB_PORT', 3306)),
    'name': os.environ.get('LAN_NANNY_DB_NAME', 'lan_nanny'),
}


# End File: lan-nanny/lan_nanny/config/hybrid.py
