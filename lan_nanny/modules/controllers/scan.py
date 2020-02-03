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
PER_PAGE = 20

@scan.route('/')
@utils.authenticate
def index():
    """Host scan roster page."""
    page = 1
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    offset = utils.get_pagination_offset(page, PER_PAGE)
    scan_hosts_collect = ScanHosts(conn, cursor)
    scan_hosts = scan_hosts_collect.get_all_paginated(limit=PER_PAGE, offset=offset)
    pagination = scan_hosts_collect.get_pagination('/scan/hosts/', page, PER_PAGE)
    data = {
        'active_page': 'scans',
        'active_page_scans': 'hosts',
        'scans':scan_hosts,
        'pagination': pagination
    }
    return render_template('scans/roster_hosts.html', **data)

@scan.route('/hosts/')
@scan.route('/hosts/<page>')
@utils.authenticate
def roster_hosts(page: str="1"):
    """Host scan roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    page = int(page)
    offset = utils.get_pagination_offset(page, PER_PAGE)
    scan_hosts_collect = ScanHosts(conn, cursor)
    scan_hosts = scan_hosts_collect.get_all_paginated(limit=PER_PAGE, offset=offset)
    pagination = scan_hosts_collect.get_pagination('/scan/hosts/', page, PER_PAGE)
    data = {
        'active_page': 'scans',
        'active_page_scans': 'hosts',
        'scans':scan_hosts,
        'pagination': pagination
    }
    return render_template('scans/roster_hosts.html', **data)

@scan.route('/ports')
@scan.route('/ports/<page>')
@utils.authenticate
def roster_ports(page: str="1"):
    """Port scan roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    page = int(page)
    offset = utils.get_pagination_offset(page, PER_PAGE)
    scan_ports_collect = ScanPorts(conn, cursor)
    scan_ports = scan_ports_collect.get_all_paginated(limit=PER_PAGE, offset=offset)
    pagination = scan_ports_collect.get_pagination('/scan/ports/', page, PER_PAGE)

    scan_ports = ScanPorts(conn, cursor).get_all()
    data = {
        'active_page': 'scans',
        'active_page_scans': 'ports',
        'scans': scan_ports,
        'pagination': pagination
    }
    return render_template('scans/roster_ports.html', **data)


@scan.route('/info/host/<scan_id>')
@utils.authenticate
def info_host(scan_id: int):
    """Info on host scan."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_host = ScanHost(conn, cursor)
    scan_host.get_by_id(scan_id)
    # device_witnesses = Witnesses(conn, cursor).get_by_scan(scan_id)
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
    return render_template('scans/info_port.html', **data)


# End File: lan-nanny/modules/controllers/scan.py
