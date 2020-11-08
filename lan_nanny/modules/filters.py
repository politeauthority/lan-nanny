"""Filters
Filters to be used in jinja templates.

"""
from datetime import datetime, timedelta

import arrow

from flask import g, Markup

from .models.device import Device
from .models.port import Port
from .models.alert import Alert
from . import utils


def time_ago(seen_at: datetime) -> str:
    """Gets a human readable 'time ago' date format. """
    if not seen_at:
        return ''
    parsed = arrow.get(seen_at)
    return parsed.humanize()


def pretty_time(first_at: datetime) -> str:
    """Gets a human readable 'time ago' date format, Mon Dec 30th 4:03:11 pm. """
    if not first_at:
        return ''
    parsed = arrow.get(first_at)
    user_time = parsed.to(g.options['timezone'].value)
    return user_time.format('ddd MMM Do h:mm:ss a')


def smart_time(date_val: datetime, format_switch_range_seconds: int = None) -> str:
    """Gets a human readable 'time ago' date format if the time is within x period, otherwise
       returns the pretty_time.
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
    """Create a switchable time display, starting with time ago value, which can be clicked to show
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
    """Draw a datetime var in "time ago" with a hidden span containing the pretty time. """
    if not the_time:
        return ''
    the_arrow = arrow.get(the_time)
    pretty_time = pretty_time_adaptive(the_time)
    html = '<div class="time_switch">'
    html += '<i class="fas fa-clock"></i>'
    html += '<span class="time-pretty">%s</span>' % arrow.get(the_time).humanize()
    html += '<span class="time-long hidden">%s</span>' % pretty_time
    html += '</div>'
    return Markup(html)

def online(seen_at: datetime) -> bool:
    """Checks to see if the device's last_seen attribute has checked in within x minutes. """
    if not seen_at:
        return False
    now = arrow.utcnow().datetime
    seen = arrow.get(seen_at).datetime

    if now - seen > timedelta(minutes=int(g.options['active-timeout'].value)):
        return False

    return True


def connected_devices(devices: list) -> int:
    """Takes a list of devices and determines the number of currently connected devices. """
    num_online = 0
    for d in devices:
        if online(d.last_seen):
            num_online += 1

    return num_online


def device_icon_status(device: Device) -> str:
    """Creates a Device's online visual representation with appropriate icons and animations based
       on a Device's current online status, with the linking and other html attributes.
    """
    now = arrow.utcnow().datetime
    seen = arrow.get(device.last_seen).datetime

    online = ''
    if now - seen < timedelta(minutes=int(g.options['active-timeout'].value)):
        online = ' connected_bolt'

    if not device.last_seen:
        online = ''

    icon = ''
    if device.icon:
        icon = '<a href="/device/info/%s"><i class="%s"></i></a>' % (
            device.id, device.icon)

    html = """
    <i class="fas fa-bolt icon-pad%(online)s"></i>
    %(icon)s
    <a href="/device/%(id)s">%(name)s</a>
    """ % {
        'icon': icon,
        'online': online,
        'id': device.id,
        'name': device.name
    }
    return Markup(html)


def alert_icon_status(alert: Alert) -> str:
    """Creates an Alert's visual status, based on if it's currently active, active but acked, or
       inactive and acked, with appropriate linking to the alert.
    """
    alert_class = "alert_resolved"
    alert_icon = "fa-exclamation-circle"

    if alert.active:
        if alert.kind == 'new-device':
            alert_class = 'alert_active_yellow'
        elif alert.acked:
            alert_class = 'alert_active_orange'
        else:
            alert_class = 'alert_active_red'
    else:
        if not alert.acked:
            alert_class = "alert_inactive_unacked_green"
        else:
            alert_class = "alert_resolved_green"
            alert_icon = "fa-check-circle"


    icon = '<a href="/alerts/info/%s"><i class="fas %s %s"></i></a>' % (
            alert.id,
            alert_icon,
            alert_class)
    return Markup(icon)


def port_online(seen_at: datetime) -> bool:
    """Checks to see if the device's last_seen attribute has checked in within x minutes. """
    if not seen_at:
        return False
    now = arrow.utcnow().datetime
    seen = arrow.get(seen_at).datetime

    if now - seen > timedelta(days=7):
        return False

    return True


def alert_pretty_kind(raw_kind: str):
    return utils.alert_pretty_kind(raw_kind)


def number(number: int) -> str:
    """Format an int as a comma broken fiscal numeric string."""
    return format(number, ",")


def get_percent(whole: int, part: int, round_ret: int=0) -> int:
    return utils.get_percent(whole, part, round_ret)


def title(the_title:str) -> str:
    """Makes the first letter of a string capitalized. """
    if not the_title:
        return the_title
    ret_title = the_title[0].upper() + the_title[1:]
    return ret_title


def round_seconds(fractional_time: float, precisision: int=2) -> float:
    """Round a float value to two points passed the decimal, or whatever is given by the
       `precision` value.
    """
    the_time = float(fractional_time)
    return round(the_time, precisision)

# End File: lan-nanny/lan_nanny/modules/filters.py
