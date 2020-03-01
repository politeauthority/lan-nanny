"""Setting Controller

"""
from flask import Blueprint, render_template, redirect, request, g
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from .. import utils
from ..models.option import Option

settings = Blueprint('Settings', __name__, url_prefix='/settings')


@settings.route('/')
@settings.route('/general')
@utils.authenticate
def form_general() -> str:
    """Setting page."""
    data = {
        'active_page': 'settings',
        'active_page_settings': 'general',
        'settings': g.options,
    }
    return render_template('settings/form_general.html', **data)


@settings.route('/save-general', methods=['POST'])
@utils.authenticate
def save_general():
    """General settings save."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    # Update timezone
    _save_setting(conn, cursor, 'timezone', request.form['settings_timezone'])

    # Save "active-timeout"
    _save_setting(conn, cursor, 'active-timeout', request.form['setting_active_timeout'])

    # Save auto-reload-console
    _save_setting(conn, cursor, 'auto-reload-console', request.form['setting_auto_reload_console'])

    # Save beta-features
    _save_setting(conn, cursor, 'beta-features', request.form['setting_beta_features'])

    return redirect('/settings')


@settings.route('/scanning')
@utils.authenticate
def form_scanning() -> str:
    """Scanning settings form page."""
    data = {
        'active_page': 'settings',
        'active_page_settings': 'scanning',
        'settings': g.options,
    }
    return render_template('settings/form_scanning.html', **data)

@settings.route('/save-scanning', methods=['POST'])
@utils.authenticate
def save_scanning():
    """Scanning settings save."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

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

    _save_setting(conn, cursor, 'scan-ports-interval', request.form['setting_scan_ports_interval'])

    return redirect('/settings/scanning')


@settings.route('/database')
@utils.authenticate
def form_database() -> str:
    """Setting page."""
    data = {
        'active_page': 'settings',
        'active_page_settings': 'database',
        'settings': g.options,
    }
    return render_template('settings/form_database.html', **data)


@settings.route('/save-database', methods=['POST'])
@utils.authenticate
def save_database():
    """Database settings save."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    _save_setting(conn, cursor, 'db-prune-days', request.form['setting_db_prune_days'])

    return redirect('/settings/database')


@settings.route('/password')
@utils.authenticate
def form_password() -> str:
    """Password setting page."""
    data = {
        'active_page': 'settings',
        'active_page_settings': 'password',
        'settings': g.options,
    }
    return render_template('settings/form_password.html', **data)


@settings.route('/save-password', methods=['POST'])
@utils.authenticate
def save_password():
    """Password settings save."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    if not check_password_hash(g.options['console-password'].value, request.form['setting_current_password']):
        return redirect('/'), 403
    if request.form['setting_password_1'] != request.form['setting_password_1']:
        return redirect('/'), 403

    new_pass = generate_password_hash(request.form['setting_password_1'], "sha256")
    _save_setting(conn, cursor, 'console-password', new_pass)

    return redirect('/settings/password')


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
