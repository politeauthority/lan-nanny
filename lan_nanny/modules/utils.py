"""Utils
Random utility functions.

"""
from datetime import datetime, timedelta
from functools import wraps
import os
import secrets
import string
import subprocess

from flask import session, redirect, g

import arrow


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.options['console-password-enabled'].value:
            return f(*args, **kwargs)
        if 'auth' not in session or not session['auth']:
            return redirect('/login'), 403
        return f(*args, **kwargs)
    return wrapper


def device_icons() -> dict:
    """
    Returns a dict keyed on font awesome CSS classes and corresponding names for those icons.

    """
    icons = {
        "fas fa-music": "Audio Device",
        "fab fa-apple": "Apple",
        "fas fa-camera": "Camera",
        "fas fa-desktop": "Desktop",
        "fas fa-gamepad": "Game Console",
        "fas fa-laptop": "Laptop",
        "fas fa-lightbulb": "Light",
        "fas fa-microchip": "Micro Controller",
        "fas fa-print": "Printer",
        "fas fa-question": "Question Mark",
        "fas fa-satellite": "Satellite",
        "fas fa-shield-alt": "Security System",
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


def device_types() -> list:
    """Get a list of all device types."""
    device_types = [
        'Audio Device', 'Camera', 'Desktop', 'Game Console', 'Laptop', 'Light', 'Micro Controller',
        'Printer', 'Security System', 'Server', 'Smart Plug', 'Smart Phone', 'Raspberry Pi', 
        'Tablet', 'Thermostat', 'Tv', 'Unknown', 'Wifi Access Point'
    ]
    return device_types


def get_size_raw(db_file_loc: str) -> str:
    """Get the size of the database on disk."""
    return os.path.getsize(db_file_loc)


def get_db_size(db_file_loc: str) -> str:
    """Get the size of a file on disk."""
    return size_of_fmt(os.path.getsize(db_file_loc))


def size_of_fmt(num: int, suffix: str = 'B') -> str:
    """Get the size of a file in human readable format. """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_active_timeout_from_now(timeout: int) -> datetime:
    """Get a datetime object representing the time from now to declare a device active."""
    now = arrow.utcnow().datetime - timedelta(minutes=timeout)
    return now


def gen_like_sql(field: str, phrase: str) -> str:
    """Generate a SQLite like statement for a given field and phrase."""
    return field + """ LIKE '%""" + phrase + """%' """


def gen_where_in_sql(ids: list) -> str:
    """Generate a where in sql safe parameter set from a list of ids."""
    ids_sql = ""
    for the_id in ids:
        ids_sql += "%s," % the_id
    ids_sql = ids_sql[:-1]
    return ids_sql

def gen_pagination_urls(base_url: str, pagination: dict) -> dict:
    """Generate pagination urls to use on the frontend."""
    pagination['first_page_url'] = _clean_url(base_url, pagination['first_page'])
    pagination['last_page_url'] = _clean_url(base_url, pagination['last_page'])
    pagination['next_page_url'] = _clean_url(base_url, pagination['next_page'])
    pagination['previous_page_url'] = _clean_url(base_url, pagination['previous_page'])
    return pagination


def get_percent(whole: int, part: int, round_ret: int=0, invert: bool=False) -> int:
    """Get the percent a part is of a whole, rounded to desired level."""
    result = part / whole * 100

    if invert:
        result = 100 - result

    if round_ret == 0:
        result = int(result)
    else:
        result = round(result, round_ret)

    return result


def key_list_on_id(some_object_list: list) -> dict:
    """
    From a list of model objects with an id attribute and return a dict keyed on the id with the
    full object set.

    """
    ret = {}
    for o in some_object_list:
        ret[o.id] = o
    return ret


def make_default_password() -> str:
    """Create a random alpha numeric string for a password."""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password


def run_shell(cmd: str) -> str:
    """Run a shell command and get a string result back."""
    result = subprocess.check_output(cmd, shell=True)
    return result.decode("utf-8")


def alert_pretty_kind(kind: str) -> str:
    if kind == 'device-offline':
        return 'Device offline'
    elif kind == 'device-online':
        return 'Device online'
    elif kind == 'new-device':
        return 'New device'
    return ''


def _clean_url(base_url: str, url: str) -> str:
    """Clean a url so its pretty and valid."""
    url =  "%s/%s" % (base_url, url)
    url = url.replace('//', '/')
    if url[0] != '/':
        url = '/' + url
    return url


# End File: lan-nanny/lan_nanny/modules/utils.py
