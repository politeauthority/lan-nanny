"""Scan - Controller

"""
import os

from flask import Blueprint, render_template
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.scan_hosts import ScanHosts
from ..collections.scan_ports import ScanPorts
from ..collections.device_witnesses import DeviceWitnesses

about = Blueprint('About', __name__, url_prefix='/about')


@about.route('/')
@utils.authenticate
def index(scan_type: str=''):
    """About page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    data = {
        'active_page': 'about',
        'db_name': os.path.normpath(app.config['LAN_NANNY_DB_FILE']),
        'db_size': utils.get_db_size(app.config['LAN_NANNY_DB_FILE']),
        'db_witness_length': DeviceWitnesses(conn, cursor).get_row_length(),
        'db_scan_host_length': ScanHosts(conn, cursor).get_row_length(),
        'db_scan_port_length': ScanPorts(conn, cursor).get_row_length()
    }
    return render_template('about.html', **data)


# End File: lan-nanny/modules/controllers/about.py
