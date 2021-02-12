"""Scan - Controller

"""
from flask import Blueprint, render_template, g
from flask import current_app as app

from .. import db
from .. import utils
from ..models.device import Device
from ..models.scan_host import ScanHost
from ..models.scan_port import ScanPort
from ..collections.devices import Devices
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.scan_hosts import ScanHosts
from ..collections.scan_ports import ScanPorts

scan = Blueprint('Scan', __name__, url_prefix='/scan')


@scan.route('/')
@utils.authenticate
def index():
    """Host scan roster page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    scan_host = ScanHost(conn, cursor)
    scan_host.get_last()
    scan_port = ScanPort(conn, cursor)
    scan_port.get_last()
    collect_scan_hosts = ScanHosts(conn, cursor)
    host_scans_last = collect_scan_hosts.get_last(10)
    host_scans_avg_24 = collect_scan_hosts.get_avg_runtime()
    collect_scan_ports = ScanPorts(conn, cursor)
    last_port_scans = collect_scan_ports.get_last(10)
    collect_devices = Devices(conn, cursor)

    # Get the Scan Port's Device object
    device_ids = get_device_ids_from_port_scans(last_port_scans)
    devices = collect_devices.get_by_ids_keyed(device_ids)

    data = {
        'host_scan_last': scan_host,
        'host_scan_avg_24': host_scans_avg_24,
        'host_scans_today': collect_scan_hosts.get_count_since(60 * 60 * 24),
        'port_scan_last': scan_port,
        'port_scans_today': collect_scan_ports.get_count_since(60 * 60 * 24),
        'last_host_scans': host_scans_last,
        'last_port_scans': last_port_scans,
        'port_devices': devices
    }
    data['active_page'] = 'scans'
    data['active_page_sub'] = 'dashboard'
    data['enable_refresh'] = True
    return render_template('scans/dashboard.html', **data)


@scan.route('/hosts/')
@scan.route('/hosts/<page>')
@utils.authenticate
def roster_hosts(page: str="1"):
    """Host scan roster page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    page = int(page)
    scan_hosts_collection = ScanHosts(conn, cursor)
    scan_pages = scan_hosts_collection.get_paginated(
        page=page,
        per_page=int(g.options['entities-per-page'].value))

    if not scan_pages['objects'] and page > 1:
        return page_not_found('Scan Hosts page not found.')

    data = {
        'scans': scan_pages['objects'],
        'pagination': utils.gen_pagination_urls('/scan/hosts/', scan_pages['info'])
    }
    data['active_page'] = 'scans'
    data['active_page_sub'] = 'hosts'
    data['enable_refresh'] = True
    return render_template('scans/roster_hosts.html', **data)


@scan.route('/ports')
@scan.route('/ports/<page>')
@utils.authenticate
def roster_ports(page: str="1"):
    """Port scan roster page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    page = int(page)
    scan_ports_collection = ScanPorts(conn, cursor)
    scan_pages = scan_ports_collection.get_paginated(
        page=page,
        per_page=int(g.options['entities-per-page'].value))
    collect_devices = Devices(conn, cursor)

    if not scan_pages['objects'] and page > 1:
        return page_not_found('Scan Ports page not found.')

    # Get the Scan Port's Device object
    device_ids = get_device_ids_from_port_scans(scan_pages['objects'])
    devices = collect_devices.get_by_ids_keyed(device_ids)
    data = {
        'scans': scan_pages['objects'],
        'pagination': utils.gen_pagination_urls('/scan/ports/', scan_pages['info']),
        'devices': devices
    }
    data['active_page'] = 'scans'
    data['active_page_sub'] = 'ports'
    data['enable_refresh'] = True
    return render_template('scans/roster_ports.html', **data)


@scan.route('/info/host/<scan_id>')
@utils.authenticate
def info_host(scan_id: int):
    """Info on host scan."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    scan_host = ScanHost(conn, cursor)
    scan_host.get_by_id(scan_id)
    device_witnesses = DeviceWitnesses(conn, cursor).get_by_scan_id(scan_id)
    data = {
        'active_page': 'scans',
        'active_page_scans': 'hosts',
        'scan': scan_host,
        'witnesses': device_witnesses,
    }
    data['enable_refresh'] = True
    return render_template('scans/info_host.html', **data)


@scan.route('/info/port/<scan_id>')
@utils.authenticate
def info_port(scan_id: int):
    """Info on host scan"""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    scan_port = ScanPort(conn, cursor)
    scan_port.get_by_id(scan_id)
    device = Device(conn, cursor)
    device.get_by_id(scan_port.device_id)
    data = {
        'active_page': 'scans',
        'scan': scan_port,
        'device': device,
    }
    data['enable_refresh'] = True
    return render_template('scans/info_port.html', **data)


def page_not_found(e: str):
    """404 Error page."""
    return render_template('errors/404.html', error=e), 404


def get_device_ids_from_port_scans(collected_port_scans: list) -> list:
    """Get device objects from a ScanPorts Collection pagination return. Device's are returned as a
       dictionary keyed on the device.id.
    """
    device_ids = []
    for port_scan in collected_port_scans:
        device_ids.append(port_scan.device_id)
    return device_ids


# End File: lan-nanny/modules/controllers/scan.py
