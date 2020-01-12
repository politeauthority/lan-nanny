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
        "fas fa-music": "Audio Device",
        "fab fa-apple": "Apple",
        "fas fa-camera": "Camera",
        "fas fa-desktop": "Desktop",
        "fas fa-laptop": "Laptop",
        "fas fa-lightbulb": "Light",
        "fad fa-microchip": "Microchip",
        "fas fa-phone": "Phone",
        "fas fa-print": "Printer",
        "fas fa-question": "Question Mark",
        "fas fa-satellite": "Satellite",
        "fas fa-server": "Sever",
        "fas fa-plug": "Smart Plug",
        "fa fa-mobile": "Smart Phone",
        # "fas fa-router": "Router",
        "fab fa-rasppberry-pi": "Raspberry Pi",
        "fas fa-tablet-alt": "Tablet",
        "fas fa-thermometer-half": "Thermostat",
        "fas fa-tv": "Tv",
        "fas fa-wifi": "Wifi Access Point",

    }
    return icons


def get_db_size(db_file_loc: str) -> str:
    """
    Gets the size of the database on disk.

    """
    return size_of_fmt(os.path.getsize(db_file_loc))


def size_of_fmt(num: int, suffix: str='B') -> str:
    """
    Gets the size of a file in human readable format.
    """
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
