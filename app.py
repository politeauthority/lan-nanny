"""App
Web application entry point.

"""

import sys

from flask import Flask, redirect, render_template, request, g

# from modules.controllers import auth as ctrl_auth
from modules.controllers.device import device as ctrl_device
from modules.controllers.alert import alert as ctrl_alert
from modules.controllers.scan import scan as ctrl_scan
from modules import db
from modules.collections.alerts import Alerts
from modules.collections.options import Options
from modules.models.option import Option
from modules.metrics import Metrics
from modules import filters


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
def close_connection(exception: str):
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
    devices = metrics.get_favorite_devices()
    all_devices = metrics.get_all_devices()
    if not devices:
        favorites = False
        devices = all_devices

    data = {}
    data['active_page'] = 'dashboard'
    data['num_connected'] = filters.connected_devices(all_devices)
    data['device_favorites'] = favorites
    data['devices'] = devices
    data['runs_over_24'] = metrics.get_runs_24_hours()
    data['last_run'] = metrics.get_last_run_log()
    return render_template('index.html', **data)


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
    # Update timezone
    option = Option(conn, cursor)
    option.name = 'timezone'
    option.value = request.form['settings_timezone']
    option.get_by_name()
    option.save()

    # Update Scan Hosts Range
    option = Option(conn, cursor)
    option.name = 'scan-hosts-range'
    option.value = request.form['setting_scan_hosts_range']
    option.get_by_name()
    option.save()
    return redirect('/settings')


@app.errorhandler(404)
def page_not_found(e: str):
    """
    404 Error page.

    """
    return render_template('errors/404.html', error=e), 404


def register_blueprints(app: Flask):
    """
    Connect the blueprints to the router.

    """

    # app.register_blueprint(ctrl_auth)
    app.register_blueprint(ctrl_device)
    app.register_blueprint(ctrl_alert)
    app.register_blueprint(ctrl_scan)


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
