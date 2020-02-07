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
from ..models.database_growth import DatabaseGrowth


about = Blueprint('About', __name__, url_prefix='/about')


@about.route('/')
@utils.authenticate
def index(scan_type: str=''):
    """About page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    growth = database_stats(conn, cursor )
    data = {
        'active_page': 'about',
        'db_name': os.path.normpath(app.config['LAN_NANNY_DB_FILE']),
        'db_size': utils.get_db_size(app.config['LAN_NANNY_DB_FILE']),
        'db_witness_length': DeviceWitnesses(conn, cursor).get_row_length(),
        'db_scan_host_length': ScanHosts(conn, cursor).get_row_length(),
        'db_scan_port_length': ScanPorts(conn, cursor).get_row_length(),
        'db_growth': growth,
    }
    return render_template('about.html', **data)


def database_stats(conn, cursor ):
    """ """
    db_current_size = utils.get_size_raw(app.config['LAN_NANNY_DB_FILE'])
    
    db_24_hours_ago = DatabaseGrowth(conn, cursor)
    db_24_hours_ago.get_24_hours_ago()

    db_delta_24 = db_current_size - db_24_hours_ago.size

    ret = {
        'db_current_size': db_current_size,
        'db_current_size_pretty': utils.size_of_fmt(db_current_size),
        'db_24_hour_size': db_24_hours_ago.size,
        'db_24_hour_size_pretty': utils.size_of_fmt(db_24_hours_ago.size),
        'db_24_hour_delta_size': db_delta_24,
        'db_24_hour_delta_size_pretty': utils.size_of_fmt(db_delta_24),

    }
    return ret

# End File: lan-nanny/lan_nanny/modules/controllers/about.py
