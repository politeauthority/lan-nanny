"""About - Controller

"""
import os
import subprocess

from flask import Blueprint, render_template, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.scan_hosts import ScanHosts
from ..collections.scan_ports import ScanPorts
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.sys_infos import SysInfos
from ..models.database_growth import DatabaseGrowth


about = Blueprint('About', __name__, url_prefix='/about')


@about.route('/')
@utils.authenticate
def index(scan_type: str=''):
    """About page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    # db_stats = database_stats(conn, cursor)
    machine_stats = get_machine_stats()
    data = {
        'active_page': 'about',
        # 'db_name': os.path.normpath(app.config['LAN_NANNY_DB_FILE']),
        'db_witness_length': DeviceWitnesses(conn, cursor).get_count_total(),
        'db_scan_host_length': ScanHosts(conn, cursor).get_count_total(),
        'db_scan_port_length': ScanPorts(conn, cursor).get_count_total(),
        # 'db_growth': db_stats,
        'machine_stats': machine_stats
    }
    return render_template('about.html', **data)


@about.route('/debug')
@utils.authenticate
def debug(scan_type: str=''):
    """Debug page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    envs = {
        'LAN_NANNY_CONFIG': os.environ.get('LAN_NANNY_CONFIG')
    }
    sys_infos = SysInfos(conn, cursor).get_all_keyed()
    data = {
        'active_page': 'about',
        'options': g.options,
        'environment': envs,
        'sys_infos': sys_infos
    }
    return render_template('debug.html', **data)

def database_stats(conn, cursor):
    """ """
    db_current_size = utils.get_size_raw(app.config['LAN_NANNY_DB_FILE'])
    
    db_24_hours_ago = DatabaseGrowth(conn, cursor)
    db_24_hours_ago.get_24_hours_ago()

    db_current = {
        'size': db_current_size,
        'size_pretty': utils.size_of_fmt(db_current_size)
    }

    db_delta_24 = {
        'size': 0,
        'size_pretty': '',
        'percent': 0,
    }

    if db_24_hours_ago.size:
        db_delta_24['size'] = db_24_hours_ago.size
        db_delta_24['size_pretty'] = utils.size_of_fmt(db_current_size - db_24_hours_ago.size)
        db_delta_24['percent'] = utils.get_percent(
            db_current['size'],
            db_delta_24['size'],
            round_ret=2,
            invert=True)
    db_first = DatabaseGrowth(conn, cursor)
    db_first.get_by_id(1)

    ret = {
        'db_first': db_first,
        'db_current': db_current,
        'db_24_hour': db_delta_24

    }
    return ret

def get_machine_stats():
    uptime = _get_uptime()

    ret = {
        'uptime': uptime
    }

    return ret

def _get_uptime():
    uptime = subprocess.check_output('uptime', shell=True)
    uptime = uptime.decode("utf-8")
    uptime = uptime[uptime.find('up') + 3:]
    return uptime


# End File: lan-nanny/lan_nanny/modules/controllers/about.py
