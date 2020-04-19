"""Device Controller

"""
from datetime import timedelta

import arrow

from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.alerts import Alerts
from ..collections.devices import Devices
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.device_ports import DevicePorts
from ..collections.scan_ports import ScanPorts
from ..models.alert import Alert
from ..models.device import Device
from ..models.entity_meta import EntityMeta
from ..metrics import Metrics

device = Blueprint('Device', __name__, url_prefix='/device')
PER_PAGE = 20


@device.route('/')
@utils.authenticate
def devices() -> str:
    """Devices roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'dashboard'
    data['devices'] = devices.get_recent()
    data['device_venders'] = Metrics(conn, cursor).get_device_vendor_grouping()
    return render_template('devices/dashboard.html', **data)


@device.route('/all')
@device.route('/all/<page>')
@utils.authenticate
def device_all(page: str="1") -> str:
    """Devices Dashboard page."""
    page = int(page)
    offset = utils.get_pagination_offset(page, PER_PAGE)
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'all'
    data['devices'] = devices.get_pagination(limit=PER_PAGE, offset=offset)
    data['pagination'] = devices.get_pagination('/device/all/', page, PER_PAGE)
    return render_template('devices/roster.html', **data)


@device.route('/online')
@device.route('/online/<page>')
@utils.authenticate
def online(page: str="1") -> str:
    """Devices roster page for only online devices."""
    app_offline_timeout = g.options['active-timeout'].value
    last_online = arrow.utcnow().datetime - timedelta(minutes=int(app_offline_timeout))
    page = int(page)
    offset = utils.get_pagination_offset(page, PER_PAGE)

    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'online'
    data['devices'] = devices.get_paginated(
        limit=PER_PAGE,
        offset=offset,
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
    data['pagination'] = devices.get_pagination_info('/device/online/', page, PER_PAGE)
    return render_template('devices/roster.html', **data)


@device.route('/offline')
@device.route('/offline/<page>')
@utils.authenticate
def offline(page: str="1") -> str:
    """Devices roster page for only online devices."""
    app_offline_timeout = g.options['active-timeout'].value
    last_online = arrow.utcnow().datetime - timedelta(minutes=int(app_offline_timeout))
    page = int(page)
    offset = utils.get_pagination_offset(page, PER_PAGE)

    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'offline'
    data['devices'] = devices.get_paginated(
        limit=PER_PAGE,
        offset=offset,
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
        }
        )
    data['pagination'] = devices.get_pagination('/device/offline/', page, PER_PAGE)
    return render_template('devices/roster.html', **data)


@device.route('/new')
@utils.authenticate
def new() -> str:
    """Devices roster page for new devices."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'new'
    data['devices'] = devices.get_new()
    return render_template('devices/roster.html', **data)


@device.route('/info/<device_id>')
@utils.authenticate
def info(device_id: int) -> str:
    """Device info page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    alerts_col = Alerts(conn, cursor)
    device_alerts = alerts_col.get_for_device(device.id)
    metrics = Metrics(conn, cursor)
    device_online_over_day = metrics.get_device_presence_over_time(device)
    device_online_over_week = metrics.get_device_presence_over_time(device, 24*7)
    device.get_ports()
    data = {}
    data['device'] = device
    data['active_page'] = 'devices'
    data['device_over_day'] = device_online_over_day
    data['device_over_week'] = device_online_over_week
    data['alerts'] = device_alerts
    return render_template('devices/info.html', **data)


@device.route('/create')
@utils.authenticate
def create() -> str:
    """Create Device form"""
    data = {}
    data['icons'] = utils.device_icons()
    data['active_page'] = 'devices'
    data['active_page_devices'] = 'create'
    data['device'] = None
    data['form'] = 'new'
    return render_template('devices/form.html', **data)


@device.route('/edit/<device_id>')
@utils.authenticate
def edit(device_id: int) -> str:
    """Device edit page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)
    icons = utils.device_icons()
    custom_icon = False
    if device.icon and device.icon not in icons:
        custom_icon = True

    data = {}
    data['device'] = device
    data['icons'] = icons
    data['device_types'] = utils.device_types()
    data['custom_icon'] = custom_icon
    data['active_page'] = 'devices'
    data['form'] = 'edit'
    return render_template('devices/form.html', **data)


@device.route('/save', methods=['POST'])
@utils.authenticate
def save():
    """Device save, route for new and editing devices."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device()
    device.conn = conn
    device.cursor = cursor
    if request.form['device_id'] == 'new':
        device.mac = request.form['device_mac']
        if not device.mac:
            return 'ERROR 422: Cannot create a device without a mac', 422
    else:
        device.get_by_id(request.form['device_id'])
        if not device.id:
            return 'ERROR 404: Route this to page_not_found method!', 404
            # return page_not_found('Device not found')

    device.name = request.form['device_name']
    device.vendor = request.form['device_vendor']
    if request.form["icon_form_choice"] == "device_icon_select":
        device.icon = request.form['device_icon_select']
        if device.icon == "none":
            device.icon = None
    else:
        device.icon = request.form['device_icon_input']

    if request.form['device_type_select'] == 'None':
        device.type = None
    else:
        device.type = request.form['device_type_select']

    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.save()

    return redirect('/device/info/%s' % device.id)


@device.route('/favorite/<device_id>')
@utils.authenticate
def favorite(device_id):
    """Web route for making a device a favorite or not."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    if device.favorite == 1:
        device.favorite = 0
    else:
        device.favorite = 1
    device.save()
    return jsonify({"success": True})


@device.route('/alert-save', methods=['POST'])
@utils.authenticate
def alert_save() -> str:
    """
    Ajax web route for update a device alert settings or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device(conn, cursor)
    device.get_by_id(request.form.get('id'))
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    if request.form.get('field_name') not in ['alert_online', 'alert_offline']:
        return jsonify("error", "Forbidden field_name %s field_name"), 403

    if request.form.get('field_value') == 'true'.lower():
        val = True
    else:
        val = False

    setattr(device, request.form.get('field_name'), val)
    device.save()
    return jsonify({"success": True})


@device.route('/quick-save', methods=['POST'])
@utils.authenticate
def quick_save() -> str:
    """
    Ajax web route for update a device alert settings or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    device = Device(conn, cursor)
    device.get_by_id(request.form.get('id'))
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')
    field_name = request.form.get('field_name')
    field_value = request.form.get('field_value')
    if field_name not in ['port_scan', 'alert_offline']:
        print("Forbidden field_name %s field_name")
        return jsonify("error", "Forbidden field_name %s field_name"), 403

    if field_value == 'true'.lower():
        val = True
    else:
        val = 0

    # Handle port_scan and alert settings differently because one is a model attr and the rest are
    # metas
    if field_name in ['port_scan']:
        setattr(device, field_value, val)
    elif field_name in ['alert_offline']:
        device.meta_update(field_name, field_value, 'bool')

    device.save()
    return jsonify({"success": True})


@device.route('/delete/<device_id>')
@utils.authenticate
def delete(device_id: int):
    """Device delete."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    # Delete the device
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    device.delete()

    # Delete device witnesses
    DeviceWitnesses(conn, cursor).delete_device(device.id)

    # Delete device ports
    DevicePorts(conn, cursor).delete_device(device.id)

    # Delete device scan ports logs
    ScanPorts(conn, cursor).delete_device(device.id)

    Alerts(conn, cursor).delete_device(device.id)

    return redirect('/device')

# End File: lan-nanny/lan_nanny/modules/controllers/device.py
