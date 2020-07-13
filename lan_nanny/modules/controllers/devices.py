"""Devices -  Controller
Handles we app for multiple devices.

"""
import csv
from datetime import timedelta
import os

import arrow

from flask import Blueprint, render_template, redirect, request, jsonify, g, Response, send_file
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.alerts import Alerts
from ..collections.devices import Devices as DevicesCollect
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.device_ports import DevicePorts
from ..collections.scan_ports import ScanPorts
from ..models.alert import Alert
from ..models.device import Device
from ..models.entity_meta import EntityMeta
from ..metrics import Metrics

devices = Blueprint('Devices', __name__, url_prefix='/devices')


@devices.route('/')
@utils.authenticate
def dashboard() -> str:
    """Devices Dashboard page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    devices = DevicesCollect(conn, cursor)
    data = {}
    data['devices'] = devices.get_recent()
    data['devices_total'] = devices.get_count_total()
    data['device_venders'] = Metrics(conn, cursor).get_device_vendor_grouping()
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'dashboard'
    data['enable_refresh'] = True
    return render_template('devices/dashboard.html', **data)


@devices.route('/all')
@devices.route('/all/<page>')
@utils.authenticate
def roster(page: str="1") -> str:
    """Devices roster pages."""
    page = int(page)

    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device_collection = DevicesCollect(conn, cursor)
    device_pages = device_collection.get_paginated(
        page=page,
        order_by={
            'field': 'last_seen',
            'op' : 'DESC'
        })

    if not device_pages['objects']:
        return page_not_found('Device page not found.')

    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'all'
    data['devices'] = device_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/devices/all/', device_pages['info'])
    data['enable_refresh'] = True
    return render_template('devices/roster.html', **data)


@devices.route('/online')
@devices.route('/online/<page>')
@utils.authenticate
def roster_online(page: str="1") -> str:
    """Devices roster page for only online devices."""
    app_offline_timeout = g.options['active-timeout'].value
    last_online = arrow.utcnow().datetime - timedelta(minutes=int(app_offline_timeout))
    page = int(page)
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    devices_collection = DevicesCollect(conn, cursor)
    device_pages = devices_collection.get_paginated(
        page=page,
        where_and=[
            {
                'field': 'last_seen',
                'value': last_online,
                'op': '>='
            }
        ],
        order_by = {
            'field': 'last_seen',
            'op' : 'DESC'
        })

    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'online'
    data['devices'] = device_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/devices/online/', device_pages['info'])
    data['enable_refresh'] = True
    return render_template('devices/roster.html', **data)


@devices.route('/offline')
@devices.route('/offline/<page>')
@utils.authenticate
def roster_offline(page: str="1") -> str:
    """Devices roster page for only online devices."""
    app_offline_timeout = g.options['active-timeout'].value
    last_online = arrow.utcnow().datetime - timedelta(minutes=int(app_offline_timeout))
    page = int(page)

    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    devices_collection = DevicesCollect(conn, cursor)
    device_pages = devices_collection.get_paginated(
        page=page,
        where_and=[
            {
                'field': 'last_seen',
                'value': last_online,
                'op': '<='
            }
        ],
        order_by = {
            'field': 'last_seen',
            'op' : 'DESC'
        })
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'offline'
    data['devices'] = device_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/devices/offline/', device_pages['info'])
    data['enable_refresh'] = True
    return render_template('devices/roster.html', **data)


@devices.route('/new')
@devices.route('/new/<page>')
@utils.authenticate
def roster_new(page: str="1") -> str:
    """Devices roster page for new devices."""
    page = int(page)
    hours_24 = arrow.utcnow().datetime - timedelta(hours=24)
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    devices_collection = DevicesCollect(conn, cursor)
    device_pages = devices_collection.get_paginated(
        page=page,
        where_and=[
            {
                'field': 'first_seen',
                'value': hours_24,
                'op': '>='
            }
        ],
        order_by = {
            'field': 'first_seen',
            'op' : 'DESC'
        })
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'new'
    data['devices'] = device_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/devices/new/', device_pages['info'])
    data['enable_refresh'] = True
    return render_template('devices/roster.html', **data)


@devices.route('/export')
@utils.authenticate
def export() -> str:
    """Devices roster page for new devices."""
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'export'
    return render_template('devices/export.html', **data)


@devices.route('/export/all')
@utils.authenticate
def export_all():
    """Export all devices as a CSV to be downloaded."""
    # Collect the data for the CSV.
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    devices = DevicesCollect(conn, cursor).get_all()
    header = [
        'id', 'name', 'mac', 'ip', 'vendor', 'device type', 'last seen', 'favorite',
        'last port scan']
    devices_csv = []
    for device in devices:
        device_row = [
            device.id, device.name, device.mac, device.ip, device.vendor, device.kind,
            device.last_seen, device.favorite]
        devices_csv.append(device_row)

    # Check that we can write the device CSV file.
    devices_csv_file = os.path.join(app.config['LAN_NANNY_TMP_DIR'], 'lan-nanny-devices.csv')
    if os.path.exists(devices_csv_file):
        os.remove(devices_csv_file)

    # Create the CSV file.
    with open(devices_csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for device_data in devices_csv:
            writer.writerow(device_data)

    return send_file(devices_csv_file, as_attachment=True)

# End File: lan-nanny/lan_nanny/modules/controllers/devices.py
