"""App
Web application entry point.

"""

import sqlite3
import sys

import arrow
from flask import Flask, redirect, render_template, request, g, jsonify
from flask_debug import Debug

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


@app.route('/device/<device_id>')
def device(device_id: int) -> str:
    """
    Device info page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    if not device.id:
        return page_not_found('Error')

    data = {}
    data['device'] = device
    data['active_page'] = 'devices'
    return render_template('devices/info.html', **data)


@app.route('/devices')
def devices() -> str:
    """
    Devices roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['devices'] = devices.get_all()
    return render_template('devices/roster.html', **data)


@app.route('/device-edit/<device_id>')
def device_edit(device_id: int) -> str:
    """
    Device edit page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    icons = utils.device_icons()

    custom_icon = False
    if device.icon and device.icon not in icons:
        custom_icon = True

    data = {}
    data['device'] = device
    data['icons'] = icons
    data['custom_icon'] = custom_icon
    data['active_page'] = 'devices'
    return render_template('devices/edit.html', **data)


@app.route('/device-save', methods=['POST'])
def device_save():
    """
    Device save.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(request.form['device_id'])

    device.name = request.form['device_name']
    device.vendor = request.form['device_vendor']
    if request.form["icon_form_choice"] == "device_icon_select":
        device.icon = request.form['device_icon_select']
        if device.icon == "none":
            device.icon = None
    else:
        device.icon = request.form['device_icon_input']

    if request.form.get('device_port_scan'):
        device.port_scan = 1
    else:
        device.port_scan = 0

    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.update()

    return redirect('/device/%s' % device.id)


@app.route('/device-favorite/<device_id>')
def device_favorite(device_id):
    """
    Web route for making a device a favorite or not.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    if device.favorite == 1:
        device.favorite = 0
    else:
        device.favorite = 1
    device.update()

    return jsonify({"success": True})


@app.route('/device-alert/<device_id>/<alert_type>/<alert_value>')
def device_alert(device_id:int, alert_type: str, alert_value: int):
    """
    Web route for making a device alert or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    if alert_type == "online":
        device.alert_online = alert_value
    elif alert_type == "offline":
        device.alert_offline = alert_value
    else:
        return jsonify({"success": False, "error": "Alert type is in correct."})

    device.update()

    return jsonify({"success": True})


@app.route('/device-delete/<device_id>')
def device_delete(device_id: int):
    """
    Device delete.

    """
    conn, cursor = db.get_db_flask(DATABASE)

    # Delete the device
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    device.delete()

    # Delete devices witness
    witness = Witness(conn, cursor)
    witness.delete_device(device.id)

    # Delete device alerts
    alert = Alert(conn, cursor)
    alert.delete_device(device.id)

    return redirect('/devices')


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
    option = Option(conn, cursor)

    utils.update_setting(option, 'timezone', request.form['settings_timezone'])
    utils.update_setting(option, 'scan-hosts-range', request.form['setting_scan_hosts_range'])
    utils.update_setting(option, 'active-timeout', request.form['setting_active_timeout'])

    return redirect('/settings')


@app.errorhandler(404)
def page_not_found(e):
    """
    404 Error page.

    """
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


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

    register_jinja_funcs(app)
    app.run(host="0.0.0.0", port=port, debug=True)


# End File: lan-nanny/app.py
