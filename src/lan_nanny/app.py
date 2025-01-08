"""App Entry Point.
Web application entry point.

"""
import os
import sys

from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import check_password_hash

from modules.controllers.api import api as ctrl_api
from modules.controllers.alerts import alerts as ctrl_alerts
from modules.controllers.devices import devices as ctrl_devices
from modules.controllers.device import device as ctrl_device
from modules.controllers.ports import ports as ctrl_ports
from modules.controllers.scan import scan as ctrl_scan
from modules.controllers.search import search as ctrl_search
from modules.controllers.about import about as ctrl_about
from modules.controllers.settings import settings as ctrl_settings
from modules.models.scan_host import ScanHost
from modules import db
from modules.collections.alerts import Alerts
from modules.collections.devices import Devices
from modules.collections.options import Options
from modules.metrics import Metrics
from modules import utils
from modules import filters

app = Flask(__name__)
if os.environ.get('LAN_NANNY_CONFIG'):
    app.config.from_object('config.%s' % os.environ.get('LAN_NANNY_CONFIG'))
else:
    app.config.from_object('config.default')


@app.before_request
def get_settings():
    """Get and loads all settings in the the flask g options namespace."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    options = Options()
    options.conn = conn
    options.cursor = cursor
    g.options = options.get_all_keyed('name')


@app.before_request
def get_active_alerts():
    """Get and loads all active alerts in the the flask g options namespace."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    alerts = Alerts(conn, cursor)
    devices = Devices(conn, cursor)
    g.alerts = alerts.get_active_unacked()
    g.alert_devices = devices.get_w_alerts(g.alerts)


@app.teardown_appcontext
def close_connection(exception: str):
    """Close SQLlite connection on app tear down."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    """Login form and form response. """
    if not request.form:
        return render_template('login.html')

    if check_password_hash(g.options['console-password'].value, request.form['password']):
        session['auth'] = True
        return redirect('/')

    return render_template('login.html', error="Incorrect password."), 403


@app.route('/forgot-password')
def forgot_password() -> str:
    """Forgotten password info page. """
    return render_template('forgot-password.html')


@app.route('/logout')
def logout():
    """Public route to logout, destroying current session auth."""
    session.pop('auth')
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(e: str):
    """404 Error page."""
    return render_template('errors/404.html', error=e), 404


@app.route('/')
@utils.authenticate
def index() -> str:
    """App dashboard for authenticated users."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    metrics = Metrics(conn, cursor)
    devices_col = Devices(conn, cursor)

    # Get favorite devices, if theres none get all devices.
    favorites = True
    fav_devices = metrics.get_favorite_devices()
    all_devices = devices_col.get_recent()
    if not fav_devices:
        favorites = False
        devices = all_devices
    else:
        devices = fav_devices

    new_devices = Devices(conn, cursor).get_new_count()
    donut_devices_online = metrics.get_dashboard_online_chart(fav_devices)

    sh = ScanHost(conn, cursor)
    sh.get_last()
    data = {}
    data['num_connected'] = devices_col.get_online_count()
    data['num_online_unidentified'] = devices_col.get_online_unidentified_count()
    data['device_favorites'] = favorites
    data['devices'] = devices
    data['new_devices'] = new_devices
    data['runs_over_24'] = metrics.get_all_scans_24()
    data['host_scan'] = sh
    data['online_donut'] = donut_devices_online
    data['active_page'] = 'dashboard'
    data['page_title'] = 'Dashboard'
    data['enable_refresh'] = True
    return render_template('dashboard.html', **data)


def register_blueprints(app: Flask):
    """Connect the blueprints to the router."""
    app.register_blueprint(ctrl_api)
    app.register_blueprint(ctrl_devices)
    app.register_blueprint(ctrl_device)
    app.register_blueprint(ctrl_alerts)
    app.register_blueprint(ctrl_ports)
    app.register_blueprint(ctrl_scan)
    app.register_blueprint(ctrl_settings)
    app.register_blueprint(ctrl_about)
    app.register_blueprint(ctrl_search)


def register_jinja_funcs(app: Flask):
    """Makes functions available to jinja templates."""
    app.jinja_env.filters['time_ago'] = filters.time_ago
    app.jinja_env.filters['pretty_time'] = filters.pretty_time
    app.jinja_env.filters['smart_time'] = filters.smart_time
    app.jinja_env.filters['online'] = filters.online
    app.jinja_env.filters['port_online'] = filters.port_online
    app.jinja_env.filters['device_icon_status'] = filters.device_icon_status
    app.jinja_env.filters['alert_icon_status'] = filters.alert_icon_status
    app.jinja_env.filters['time_switch'] = filters.time_switch
    app.jinja_env.filters['alert_pretty_kind'] = filters.alert_pretty_kind
    app.jinja_env.filters['number'] = filters.number
    app.jinja_env.filters['get_percent'] = filters.get_percent
    app.jinja_env.filters['round_seconds'] = filters.round_seconds


if __name__ == '__main__':
    port = app.config['APP_PORT']
    if len(sys.argv) > 1:
        port = sys.argv[1]
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    register_blueprints(app)
    register_jinja_funcs(app)
    # install()
    app.run(host="0.0.0.0", port=port, debug=True)


# End File: lan-nanny/lan_nanny/app.py
