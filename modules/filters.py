"""Filters
Filters to be used in jinja templates.

"""
import arrow

def last_seen(seen_at):
    """
    Gets a human readable 'time ago' date format.

    """
    parsed = arrow.get(seen_at)
    return parsed.humanize()

# End File: lan-nanny/modules/filters.py
