"""Filters
Filters to be used in jinja templates.

"""
from datetime import datetime, timedelta

import arrow

from flask import g

from app import app

def time_ago(seen_at: datetime) -> str:
    """
    Gets a human readable 'time ago' date format.

    """
    if not seen_at:
        return  ''
    parsed = arrow.get(seen_at)
    return parsed.humanize()


def pretty_time(first_at: datetime) -> str:
    """
    Gets a human readable 'time ago' date format, Mon Dec 30th 4:03:11 pm

    """
    parsed = arrow.get(first_at)
    user_time = parsed.to(g.options['timezone'].value)
    return user_time.format('ddd MMM Do h:mm:ss a')


def smart_time(date_val: datetime, format_switch_range_seconds: int=None) -> str:
    """
    Gets a human readable 'time ago' date format if the time is within x period, otherwise returns the pretty_time.

    """
    if not date_val:
        return  ''
    parsed = arrow.get(date_val)
    if not format_switch_range_seconds:
        format_switch_range_seconds = (60 * 60) * 12 # default 12 hours

    delta = arrow.utcnow().datetime - parsed.datetime

    if delta.seconds > format_switch_range_seconds:
        return pretty_time(date_val)
    else:
        return parsed.humanize()


def online(seen_at: datetime) -> bool:
    """
    Checks to see if the device's last_seen attribute has checked in within x minutes.

    """
    now = arrow.utcnow().datetime
    seen = arrow.get(seen_at).datetime

    if now - seen > timedelta(minutes=int(g.options['active-timeout'].value)):
        return False

    return True

def connected_devices(devices: list) -> int:
    """
    Takes a list of devices and determines the number of currently connected devices.

    """
    num_online = 0
    for d in devices:
        if online(d.last_seen):
            num_online += 1

    return num_online

# End File: lan-nanny/modules/filters.py
