"""Default configs

"""
import os

DEBUG = False
APP_PORT = 5000
LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_SCAN_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_scan.log')
LAN_NANNY_WEB_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_web.log')
LAN_NANNY_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'pass': 'password',
    'port': 3306,
    'name': 'lan_nanny'
}


LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'pass': 'password',
    'port': 3306,
    'name': 'lan_nanny'
}


# End File: lan-nanny/lan_nanny/config/default.py
