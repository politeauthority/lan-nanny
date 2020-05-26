"""Device Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.alerts import Alerts
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.device_ports import DevicePorts
from ..collections.scan_ports import ScanPorts
from ..models.device import Device
from ..metrics import Metrics

device = Blueprint('Device', __name__, url_prefix='/device')


@device.route('/<device_id>')
@utils.authenticate
def info(device_id: int) -> str:
    """Device info page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return page_not_found('Device not found')

    alerts_col = Alerts(conn, cursor)
    device_alerts = alerts_col.get_for_device(device.id)
    metrics = Metrics(conn, cursor)
    device_online_over_day = metrics.get_device_presence_over_time(device)
    device_online_over_week = metrics.get_device_presence_over_time(device, 24*7)
    device.get_ports()
    data = {}
    data['device'] = device
    data['active_page'] = 'devices'
    data['active_page_device'] = 'general'
    data['device_over_day'] = device_online_over_day
    data['device_over_week'] = device_online_over_week
    data['alerts'] = device_alerts
    return render_template('device/info.html', **data)


@device.route('/ports/<device_id>')
@utils.authenticate
def info_ports(device_id: int) -> str:
    """Device info ports sub page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return page_not_found('Device not found')

    device.get_ports()

    scan_ports_log = ScanPorts(conn, cursor).get_by_device_id(device.id)

    data = {}
    data['device'] = device
    data['scan_ports'] = scan_ports_log
    data['active_page'] = 'devices'
    data['active_page_device'] = 'ports'
    return render_template('device/ports.html', **data)


@device.route('/options/<device_id>')
@utils.authenticate
def info_options(device_id: int) -> str:
    """Device info ports sub page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return page_not_found('Device not found')

    data = {}
    data['device'] = device
    data['active_page'] = 'devices'
    data['active_page_device'] = 'options'
    return render_template('device/options.html', **data)

@device.route('/edit/<device_id>')
@utils.authenticate
def edit(device_id: int) -> str:
    """Device edit page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
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
    data['form'] = 'edit'
    data['active_page'] = 'devices'
    data['active_page_device'] = 'edit'
    return render_template('device/edit.html', **data)


@device.route('/save', methods=['POST'])
@utils.authenticate
def save():
    """Device save, route for new and editing devices."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device()
    device.conn = conn
    device.cursor = cursor
    if request.form['device_id'] == 'new':
        device.mac = request.form['device_mac']
        device.last_seen = None
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
        device.kind = None
    else:
        device.kind = request.form['device_type_select']

    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.save()

    return redirect('/device/%s' % device.id)


@device.route('/favorite/<device_id>')
@utils.authenticate
def favorite(device_id):
    """Web route for making a device a favorite or not."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
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


@device.route('/quick-save', methods=['POST'])
@utils.authenticate
def quick_save() -> str:
    """Ajax web route for update a device alert settings or not when coming on or off the network.
    """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device(conn, cursor)
    device.get_by_id(request.form.get('id'))
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')
    field_name = request.form.get('field_name')
    field_value = request.form.get('field_value')
    if field_name not in ['port_scan', 'alert_offline', 'alert_online', 'alert_jitter']:
        logging.warning("Forbidden field_name %s field_name")
        return jsonify("error", "Forbidden field_name %s field_name"), 403


    if field_name in ['port_scan', 'alert_online', 'alert_offline']:
        if field_value == 'true'.lower():
            field_value = 1
        else:
            field_value = 0

    # Handle port_scan and alert settings differently because one is a model attr and the rest are
    # metas
    if field_name == 'port_scan':
        setattr(device, field_name, val)
    elif field_name in ['alert_offline', 'alert_online']:
        device.meta_update(field_name, field_value, 'bool')
    elif field_name == 'alert_jitter':
        if field_value:
            device.meta_update(field_name, field_value, 'int')
        else:
            device.meta_delete(field_name)

    device.save()
    return jsonify({"success": True})


@device.route('/delete/<device_id>')
@utils.authenticate
def delete(device_id: int):
    """Device delete."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
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
    return redirect('/devices')


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
    return render_template('device/create.html', **data)


def page_not_found(e: str):
    """404 Error page."""
    return render_template('errors/404.html', error=e), 404

# End File: lan-nanny/lan_nanny/modules/controllers/device.py
