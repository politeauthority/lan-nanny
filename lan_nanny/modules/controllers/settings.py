"""Settings Controller

"""
from flask import Blueprint, render_template, redirect, request, g
from flask import current_app as app

from .. import db
from ..models.option import Option

settings = Blueprint('Settings', __name__, url_prefix='/settings')


@settings.route('/')
def basic() -> str:
    """
    Settings page.

    """
    data = {
        'active_page': 'settings',
        'settings': g.options,
    }
    return render_template('settings/basic_form.html', **data)


@settings.route('/save', methods=['POST'])
def settings_save():
    """
    Settings save.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    # Update timezone
    option = Option(conn, cursor)
    option.name = 'timezone'
    option.get_by_name()
    option.value = request.form['settings_timezone']
    option.save()

    # Update Scan Hosts Range
    option = Option(conn, cursor)
    option.name = 'scan-hosts-range'
    option.get_by_name()
    option.value = request.form['setting_scan_hosts_range']
    option.save()

    _save_setting(
        conn,
        cursor,
        'scan-hosts-enabled',
        request.form['setting_scan_hosts_enabled'],
        'bool')

    return redirect('/settings')


def _save_setting(conn, cursor, option_name, option_value, option_type):
    """
    """
    option = Option(conn, cursor)
    option.name = option_name
    option.id = g.options[option_name].id
    if option_type == 'bool':
        if option_value == 'true':
            option.value = 1
        elif option_value == 'false':
            option.value = 0
    else:
        option.value = option_value
    option.save()


# End File: lan-nanny/lan_nanny/modules/controllers/settings.py
