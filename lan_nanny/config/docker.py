"""Docker configs

"""
import os

DEBUG = True
APP_PORT = int(os.environ.get('LAN_NANNY_APP_PORT', 5000))
LAN_NANNY_TMP_DIR = "/tmp"
LAN_NANNY_SCAN_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_scan.log')
LAN_NANNY_WEB_LOG = os.path.join(LAN_NANNY_TMP_DIR, 'lan_nanny_web.log')
LAN_NANNY_DB = {
    'host': os.environ.get('LAN_NANNY_DB_HOST'),
    'user': os.environ.get('LAN_NANNY_DB_USER'),
    'pass': os.environ.get('LAN_NANNY_DB_PASS'),
    'port': int(os.environ.get('LAN_NANNY_DB_PORT', 3306)),
    'name': os.environ.get('LAN_NANNY_DB_NAME'),
}


# End File: lan-nanny/lan_nanny/config/docker.py
