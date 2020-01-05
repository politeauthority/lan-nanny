"""Utils
Random utility functions.

"""
from datetime import datetime, timedelta
import os

import arrow


def device_icons() -> dict:
    """
    Returns a dict keyed on font awesome CSS classes and corresponding names for those icons.

    """
    icons = {
        "fab fa-apple": "Apple",
        "fab fa-rasppberry-pi": "Raspberry Pi",
        "fas fa-print": "Printer",
        "fas fa-tablet-alt": "Tablet",
        "fas fa-plug": "Smart Plug",
        "fas fa-laptop": "Laptop",
        "fas fa-question": "Question Mark",
        "fas fa-satellite": "Satellite",
        "fas fa-music": "Audio Device",
        "fas fa-camera": "Camera",
        "fas fa-tv": "Tv",
        "fas fa-phone": "Phone"
    }
    return icons


def get_db_size(db_file_loc: str):
    """
    """
    return sizeof_fmt(os.path.getsize(db_file_loc))


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_active_timeout_from_now(timeout: int) -> datetime:
    """
    Gets a datetime object representing the time from now to declare a device active.

    """
    now = arrow.utcnow().datetime - timedelta(minutes=timeout)
    return now

# End File: lan-nanny/lan_nanny/modules/utils.py
