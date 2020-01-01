"""Utils
Random utility functions.

"""
from flask import g

from .models.option import Option


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
    }
    return icons


def update_setting(option: Option, setting_name:str, setting_value:str):
    """
    """
    option.id = g.options[setting_name].id
    option.value = setting_value
    option.update()


# End File: lan-nanny/modules/utils.py
