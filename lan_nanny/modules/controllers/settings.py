"""Setting Controller

"""
from flask import Blueprint, render_template, redirect, request, g
from flask import current_app as app

from .. import db
from .. import utils
from ..models.option import Option

settings = Blueprint('Settings', __name__, url_prefix='/settings')


@settings.route('/')
@utils.authenticate
def basic() -> str:
    """Setting page."""
    data = {
        'active_page': 'settings',
        'settings': g.options,
    }
    return render_template('settings/basic_form.html', **data)


@settings.route('/save', methods=['POST'])
@utils.authenticate
def settings_save():
    """Settings save."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    # General Settings
    # Update timezone
    _save_setting(conn, cursor, 'timezone', request.form['settings_timezone'])
    # Save "active-timeout"
    _save_setting(conn, cursor, 'active-timeout', request.form['setting_active_timeout'])
    # Save beta-features
    _save_setting(conn, cursor, 'beta-features', request.form['setting_beta_features'])

    # Scan Settings
    # Save "scan-hosts-range"
    _save_setting(conn, cursor, 'scan-hosts-range', request.form['setting_scan_hosts_range'])
    # Save "scan-hosts-enabled"
    _save_setting(conn, cursor, 'scan-hosts-enabled', request.form['setting_scan_hosts_enabled'])
    # Save "scan-ports-enabled"
    _save_setting(conn, cursor, 'scan-ports-enabled', request.form['setting_scan_ports_enabled'])
    # Save "scan-scan-ports-per-run"
    _save_setting(
        conn,
        cursor,
        'scan-ports-per-run',
        request.form['setting_scan_ports_per_run'])

    _save_setting(conn, cursor, 'scan-ports-default', request.form['setting_scan_ports_default'])

    return redirect('/settings')


def _save_setting(conn, cursor, option_name, option_value):
    """
    """
    option = g.options[option_name]
    option.conn = conn
    option.cursor = cursor
    if option.value == option_value:
        return True
    option.value = option_value
    option.update()
    return True


# End File: lan-nanny/lan_nanny/modules/controllers/settings.py
