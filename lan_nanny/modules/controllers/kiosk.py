"""Kiosk - Controller

"""

from flask import Blueprint, render_template, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.devices import Devices as DevicesCollect
from modules.models.scan_host import ScanHost
from modules.metrics import Metrics


kiosk = Blueprint('Kiosk', __name__, url_prefix='/kiosk')


@kiosk.route('/')
# @utils.authenticate
def index(scan_type: str=''):
    """Kiosk Index page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    metrics = Metrics(conn, cursor)
    sh = ScanHost(conn, cursor).get_last()
    devices_col = DevicesCollect(conn, cursor)

    # Get favorite devices, if theres none get all devices.
    favorites = True
    fav_devices = metrics.get_favorite_devices()
    all_devices = devices_col.get_recent()
    if not fav_devices:
        favorites = False
        devices = all_devices
    else:
        devices = fav_devices

    donut_devices_online = metrics.get_dashboard_online_chart(fav_devices)
    devices_new_count = devices_col.get_new_count()
    # if devices_new_count > 0:
    data = {}
    data['devices'] = devices
    data['num_connected'] = devices_col.get_online_count()
    data['num_new_devices'] = devices_col.get_new_count()
    data['online_donut'] = metrics.get_dashboard_online_chart(fav_devices)
    data['runs_over_24'] = metrics.get_all_scans_24()
    data['host_scan'] = sh
    return render_template('kiosk.html', **data)


# End File: lan-nanny/lan_nanny/modules/controllers/kiosk.py
