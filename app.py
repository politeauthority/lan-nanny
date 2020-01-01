"""App
Web application entry point.

"""

import sqlite3
import sys

import arrow
from flask import Flask, redirect, render_template, request, g, jsonify
from flask_debug import Debug

# from modules.controllers import auth as ctrl_auth
from modules.controllers.device import device as ctrl_device
from modules import db
from modules.models.device import Device
from modules.models.option import Option
from modules.models.alert import Alert
from modules.models.run_log import RunLog
from modules.models.witness import Witness
from modules.collections.devices import Devices
from modules.collections.alerts import Alerts
from modules.collections.options import Options
from modules.collections.run_logs import RunLogs
from modules.metrics import Metrics
from modules import filters
from modules import utils


DATABASE = "lan_nanny.db"
app = Flask(__name__)


@app.before_request
def get_settings():
    """
    Gets and loads all settings in the the flask g options namespace.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    options = Options()
    options.conn = conn
    options.cursor = cursor
    g.options = options.get_all_keyed()


@app.before_request
def get_alerts():
    """
    Gets and loads all active alerts in the the flask g options namespace.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alerts = Alerts(conn, cursor)
    g.alerts = alerts.get_active_unacked(build_devices=True)


@app.teardown_appcontext
def close_connection(exception):
    """
    Close SQLlite connection on app tear down.

    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index() -> str:
    """
    App home page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    metrics = Metrics(conn, cursor)

    # Get favorite devices, if theres none get all devices.
    favorites = True
    devices =  metrics.get_favorite_devices()
    all_devices = metrics.get_all_devices()
    if not devices:
        favorites =  False
        devices = all_devices

    data = {}
    data['active_page'] = 'dashboard'
    data['num_connected'] = filters.connected_devices(all_devices)
    data['device_favorites'] = favorites
    data['devices'] = devices
    data['runs_over_24'] = metrics.get_runs_24_hours()
    data['last_run'] = metrics.get_last_run_log()
    return render_template('index.html', **data)


@app.route('/alerts')
def alerts():
    """
    Alerts roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alerts = Alerts(conn, cursor)
    data = {}
    data['alerts'] = alerts.get_all()
    data['active_page'] = 'alerts'
    return render_template('alerts/roster.html', **data)


@app.route('/alert-info/<alert_id>')
def alert_info(alert_id: int):
    """
    Alert info page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id, build_device=True)
    if not alert.id:
        return page_not_found('Alert not found')

    if not alert.acked:
        alert.acked = 1
        alert.acked_ts = arrow.utcnow().datetime
        alert.save()
    data = {}
    data['active_page'] = 'alert-info'
    data['alert'] = alert
    data['active_page'] = 'alerts'
    return render_template('alerts/info.html', **data)

@app.route('/scans')
def scans():
    """
    Scans roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    run_logs = RunLogs(conn, cursor)
    data = {
        'active_page': 'scans',
        'scans': run_logs.get_all()
    }
    return render_template('scans/roster.html', **data)


@app.route('/scan/<scan_id>')
def scan(scan_id):
    """
    Scan info page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    run_log = RunLog(conn, cursor)
    scan = run_log.get_by_id(scan_id)
    data = {}
    data['active_page'] = 'scans'
    data['scan'] = scan

    return render_template('scans/info.html', **data)

@app.route('/settings')
def settings() -> str:
    """
    Settings page.

    """
    data = {
        'active_page': 'settings',
        'settings': g.options,
    }
    return render_template('settings.html', **data)


@app.route('/settings-save', methods=['POST'])
def settings_save():
    """
    Settings save.

    """
    conn, cursor = db.get_db_flask(DATABASE)

    utils.update_setting(conn, cursor, 'timezone', request.form['settings_timezone'])
    utils.update_setting(conn, cursor, 'scan-hosts-range', request.form['setting_scan_hosts_range'])
    # utils.update_setting(conn, cursor, 'active-timeout', request.form['setting_active_timeout'])
    #

    return redirect('/settings')


@app.errorhandler(404)
def page_not_found(e):
    """
    404 Error page.

    """
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


def register_blueprints(app):
    """
    Connect the blueprints to the router.

    """

    # app.register_blueprint(ctrl_auth)
    app.register_blueprint(ctrl_device)


def register_jinja_funcs(app: Flask):
    """
    Makes functions available to jinja templates.

    """
    app.jinja_env.filters['time_ago'] = filters.time_ago
    app.jinja_env.filters['pretty_time'] = filters.pretty_time
    app.jinja_env.filters['smart_time'] = filters.smart_time
    app.jinja_env.filters['online'] = filters.online


if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]

    register_blueprints(app)
    register_jinja_funcs(app)
    app.run(host="0.0.0.0", port=port, debug=True)


# End File: lan-nanny/app.py
