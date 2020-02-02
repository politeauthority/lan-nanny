"""Scan - Controller

"""
from flask import Blueprint, render_template
from flask import current_app as app

from .. import db
from .. import utils
from ..models.scan_host import ScanHost
from ..models.scan_port import ScanPort
from ..collections.scan_hosts import ScanHosts
from ..collections.scan_ports import ScanPorts

scan = Blueprint('Scan', __name__, url_prefix='/scan')


@scan.route('/')
@utils.authenticate
def roster_hosts():
    """Host scan roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_hosts = ScanHosts(conn, cursor).get_all()
    data = {
        'active_page': 'scans',
        'active_page_scans': 'hosts',
        'scans':scan_hosts
    }
    return render_template('scans/roster_hosts.html', **data)

@scan.route('/ports')
@utils.authenticate
def roster_ports():
    """Port scan roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_ports = ScanPorts(conn, cursor).get_all()
    data = {
        'active_page': 'scans',
        'active_page_scans': 'ports',
        'scans':scan_ports
    }
    return render_template('scans/roster_ports.html', **data)


@scan.route('/info/host/<scan_id>')
@utils.authenticate
def info_host(scan_id: int):
    """Info on host scan."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_host = ScanHost(conn, cursor).get_by_id(scan_id)
    data = {
        'active_page': 'scans',
        'active_page_scans': 'hosts',
        'scan': scan_host
    }
    return render_template('scans/info_host.html', **data)


@scan.route('/info/port/<scan_id>')
@utils.authenticate
def info_port(scan_id: int):
    """Info on host scan"""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_port = ScanPort(conn, cursor).get_by_id(scan_id)
    data = {
        'active_page': 'scans',
        'scan': scan_port
    }
    return render_template('scans/info_host.html', **data)

# End File: lan-nanny/modules/controllers/scan.py
