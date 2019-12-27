"""Filters
Filters to be used in jinja templates.

"""
from datetime import datetime, timedelta

import arrow

from flask import g

from app import app

def time_ago(seen_at) -> str:
    """
    Gets a human readable 'time ago' date format.

    """
    parsed = arrow.get(seen_at)
    return parsed.humanize()


def first_seen(first_at) -> str:
    """
    Gets a human readable 'time ago' date format.

    """
    parsed = arrow.get(first_at)
    user_time = parsed.to(g.options['timezone'].value)
    return user_time.format('ddd MMM Do h:mm:ss a')


def online(seen_at):
    """
    Checks to see if the device's last_seen attribute has checked in within x minutes.

    """
    now = arrow.utcnow().datetime
    seen = arrow.get(seen_at).datetime

    if now - seen > timedelta(minutes=5):
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
