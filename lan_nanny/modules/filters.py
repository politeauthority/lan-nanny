"""Filters
Filters to be used in jinja templates.

"""
from datetime import datetime, timedelta

import arrow

from flask import g, Markup

from .models.device import Device
from .models.port import Port


def time_ago(seen_at: datetime) -> str:
    """
    Gets a human readable 'time ago' date format.

    """
    if not seen_at:
        return ''
    parsed = arrow.get(seen_at)
    return parsed.humanize()


def pretty_time(first_at: datetime) -> str:
    """
    Gets a human readable 'time ago' date format, Mon Dec 30th 4:03:11 pm

    """
    if not first_at:
        return ''
    parsed = arrow.get(first_at)
    user_time = parsed.to(g.options['timezone'].value)
    return user_time.format('ddd MMM Do h:mm:ss a')


def smart_time(date_val: datetime, format_switch_range_seconds: int = None) -> str:
    """
    Gets a human readable 'time ago' date format if the time is within x period, otherwise returns
    the pretty_time.

    """
    if not date_val:
        return ''
    parsed = arrow.get(date_val)
    if not format_switch_range_seconds:
        format_switch_range_seconds = (60 * 60) * 12  # default 12 hours

    delta = arrow.utcnow().datetime - parsed.datetime

    if delta.seconds > format_switch_range_seconds:
        return pretty_time(date_val)
    else:
        return parsed.humanize()


def pretty_time_adaptive(date_val: datetime) -> str:
    """
    Create a switchable time display, starting with time ago value, which can be clicked to show
    a more standard date value via javascript.

    """
    if not date_val:
        return ''
    parsed = arrow.get(date_val)
    parsed = parsed.to(g.options['timezone'].value)
    format_switch_range_seconds = (60 * 60) * 12  # default 12 hours

    delta = arrow.utcnow().datetime - parsed.datetime

    if delta.seconds > format_switch_range_seconds:
        return parsed.format('ddd MMM Do h:mm:ss a')
    else:
        return parsed.format('h:mm:ss a')


def time_switch(the_time) -> str:
    """Draw a datetime var in "time ago" with a hidden span containing the pretty time."""
    the_arrow = arrow.get(the_time)
    pretty_time = pretty_time_adaptive(the_time)
    html = '<div class="time_switch">'
    html += '<i class="fas fa-clock"></i>'
    html += '<span class="time-pretty">%s</span>' % arrow.get(the_time).humanize()
    html += '<span class="time-long hidden">%s</span>' % pretty_time
    html += '</div>'
    return Markup(html)

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


def device_icon_status(device: Device) -> int:
    """
    Takes a list of devices and determines the number of currently connected devices.

    """
    now = arrow.utcnow().datetime
    seen = arrow.get(device.last_seen).datetime

    online = ''
    if now - seen < timedelta(minutes=int(g.options['active-timeout'].value)):
        online = ' connected_bolt'

    icon = ''
    if device.icon:
        icon = '<a href="/device/info/%s"><i class="%s"></i></a>' % (
            device.id, device.icon)

    html = """
    <i class="fas fa-bolt icon-pad%(online)s"></i>
    %(icon)s
    <a href="/device/info/%(id)s">%(name)s</a>
    """ % {
        'icon': icon,
        'online': online,
        'id': device.id,
        'name': device.name
    }
    return Markup(html)


def number(number: int) -> str:
    """Format an int as a comma broken fiscal numeric string."""
    return format(number, ",")

# End File: lan-nanny/lan_nanny/modules/filters.py
