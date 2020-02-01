"""App Entry Point.
Web application entry point.

"""

import os
import sys

from flask import Flask, render_template, request, redirect, session, g

from modules.controllers.alert import alert as ctrl_alert
from modules.controllers.device import device as ctrl_device
from modules.controllers.ports import ports as ctrl_ports
from modules.controllers.scan import scan as ctrl_scan
from modules.controllers.search import search as ctrl_search
from modules.controllers.about import about as ctrl_about
from modules.controllers.settings import settings as ctrl_settings
from modules import db
from modules.collections.alerts import Alerts
from modules.collections.devices import Devices
from modules.collections.options import Options
from modules.collections.witnesses import Witnesses
from modules.collections.scan_hosts import ScanHosts
from modules.metrics import Metrics
from modules import utils
from modules import filters
from config import default as default_config_obj

app = Flask(__name__)
app.config.from_object(default_config_obj)


@app.before_request
def get_settings():
    """Get and loads all settings in the the flask g options namespace."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    options = Options()
    options.conn = conn
    options.cursor = cursor
    g.options = options.get_all_keyed()


@app.before_request
def get_active_alerts():
    """Get and loads all active alerts in the the flask g options namespace."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alerts = Alerts(conn, cursor)
    g.alerts = alerts.get_active_unacked(build_devices=True)


@app.teardown_appcontext
def close_connection(exception: str):
    """Close SQLlite connection on app tear down."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login form and form response"""
    if not request.form:
        return render_template('login.html')

    print(request.form['password'])
    print(g.options['console-password'].value)
    if request.form['password'] == g.options['console-password'].value:
        session['auth'] = True
        return redirect('/')

    return render_template('login.html', error="Incorrect password."), 403


@app.route('/')
@utils.authenticate
def index() -> str:
    """App dashboard."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    metrics = Metrics(conn, cursor)

    # Get favorite devices, if theres none get all devices.
    # @todo filter already selected devices, not two pulls from db
    favorites = True
    fav_devices = metrics.get_favorite_devices()
    all_devices = metrics.get_all_devices()
    if not fav_devices:
        favorites = False
        devices = all_devices
    else:
        devices = fav_devices

    new_devices = Devices(conn, cursor).get_new_count()
    donut_devices_online = metrics.get_dashboard_online_chart(fav_devices)

    data = {}
    data['active_page'] = 'dashboard'
    data['num_connected'] = filters.connected_devices(all_devices)
    data['device_favorites'] = favorites
    data['devices'] = devices
    data['new_devices'] = new_devices
    data['runs_over_24'] = metrics.get_scan_host_runs_24_hours()
    data['host_scan'] = metrics.get_last_host_scan()
    data['online_donut'] = donut_devices_online
    return render_template('dashboard.html', **data)


# @app.route('/about')
# @utils.authenticate
# def about() -> str:
#     """About page."""
#     conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
#     data = {
#         'active_page': 'about',
#         'db_name': os.path.normpath(app.config['LAN_NANNY_DB_FILE']),
#         'db_size': utils.get_db_size(app.config['LAN_NANNY_DB_FILE']),
#         'db_witness_length': Witnesses(conn, cursor).get_row_length(),
#         'db_host_scan_length': ScanHosts(conn, cursor).get_row_length()
#     }
#     return render_template('about.html', **data)


@app.route('/logout')
def logout():
    """Public route to logout, destroying current session auth."""
    session.pop('auth')
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(e: str):
    """404 Error page."""
    return render_template('errors/404.html', error=e), 404


def register_blueprints(app: Flask):
    """Connect the blueprints to the router."""
    app.register_blueprint(ctrl_device)
    app.register_blueprint(ctrl_alert)
    app.register_blueprint(ctrl_ports)
    app.register_blueprint(ctrl_scan)
    app.register_blueprint(ctrl_settings)
    app.register_blueprint(ctrl_about)
    app.register_blueprint(ctrl_search)
    # app.register_blueprint(ctrl_auth)


def register_jinja_funcs(app: Flask):
    """Makes functions available to jinja templates."""
    app.jinja_env.filters['time_ago'] = filters.time_ago
    app.jinja_env.filters['pretty_time'] = filters.pretty_time
    app.jinja_env.filters['smart_time'] = filters.smart_time
    app.jinja_env.filters['online'] = filters.online
    app.jinja_env.filters['device_icon_status'] = filters.device_icon_status
    app.jinja_env.filters['time_switch'] = filters.time_switch
    app.jinja_env.filters['number'] = filters.number


if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    register_blueprints(app)
    register_jinja_funcs(app)
    # install()
    app.run(host="0.0.0.0", port=port, debug=True)


# End File: lan-nanny/lan_nanny/app.py
