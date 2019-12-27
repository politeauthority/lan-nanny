"""App
Web application entry point.

"""

import sqlite3
import sys

from modules import db
from modules.device import Device
from modules.devices import Devices
from modules.option import Option
from modules.options import Options
from modules.run_logs import RunLogs
from modules.metrics import Metrics
from modules.collections.alerts import Alerts
from modules import filters

from flask import Flask, redirect, render_template, request, g, jsonify
from flask_debug import Debug

app = Flask(__name__)
# Debug(app)
# app.run(debug=True)

DATABASE = "lan_nanny.db"


@app.before_request
def get_settings():
    """
    Gets and loads all settings in the the flask g options namespace.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    options = Options()
    options.conn = conn
    options.cursor = cursor

    opt_dict = {}
    all_options = options.get_all()
    for option in all_options:
        opt_dict[option.name] = option
    g.options = opt_dict


@app.before_request
def get_alerts():
    """
    Gets and loads all active alerts in the the flask g options namespace.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alerts = Alerts(conn, cursor)
    g.alerts = alerts.get_active()


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

    data = {}
    data['active_page'] = 'device'
    data['device'] = device
    return render_template('device.html', **data)


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
    return render_template('device_roster.html', **data)


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

    icons = _device_icons()

    custom_icon = False
    if device.icon and device.icon not in icons:
        custom_icon = True

    data = {}
    data['device'] = device
    data['icons'] = icons
    data['custom_icon'] = custom_icon
    return render_template('device_edit.html', **data)


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

    device.alert_online = _device_alert_checkbox_value('device_alert_online', request.form)
    device.alert_offline = _device_alert_checkbox_value('device_alert_offline', request.form)

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
    option = Option()
    option.conn = conn
    option.cursor = cursor


    # Save the timezone value
    option.name = 'timezone'
    option.value = request.form['settings_timezone']
    option.update()

    return redirect('/settings')

@app.route('/alerts')
def alerts():
    """
    Alerts roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alerts = Alerts(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['alerts'] = alerts.get_all()
    return render_template('alerts_roster.html', **data)


def register_jinja_funcs(app: Flask):
    """
    Makes functions available to jinja templates.

    """
    app.jinja_env.filters['time_ago'] = filters.time_ago
    app.jinja_env.filters['first_seen'] = filters.first_seen
    app.jinja_env.filters['online'] = filters.online


def _device_icons() -> dict:
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
        "fas fa-satellite": "Satellite"
    }
    return icons

def _device_alert_checkbox_value(name, form):
    """
    """
    if name in form:
        if form[name] == "on":
            return 1
    return 0

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]

    register_jinja_funcs(app)
    app.run(host="0.0.0.0", port=port, debug=True)


# End File: lan-nanny/app.py
