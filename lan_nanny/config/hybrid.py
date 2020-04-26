"""Hybrid config
This config should be used if you have an existing MySQL database to use, and LanNanny is not
running inside a docker container, but directly on the host machine.
To use the config set the environment variable LAN_NANNY_CONFIG=hybrid

"""
import os

DEBUG = True
APP_PORT = 5000
LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_SCAN_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_scan.log')
LAN_NANNY_WEB_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_web.log')
LAN_NANNY_DB = {
    'host': '127.0.0.1',
    'user': 'user',
    'pass': 'password',
    'port': 3306,
    'name': 'lan_nanny'
}


# End File: lan-nanny/lan_nanny/config/hybrid.py
