"""Device Controller

"""
from datetime import timedelta

import arrow

from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.alerts import Alerts
from ..collections.device_macs import DeviceMacs as CollectDeviceMacs
from ..collections.device_witnesses import DeviceWitnesses
from ..collections.device_ports import DevicePorts
from ..collections.scan_ports import ScanPorts
from ..models.device import Device
from ..models.device_mac import DeviceMac
from ..models.entity_meta import EntityMeta
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
    ports = _filter_device_ports_info(device)
    data = {}
    data['device'] = device
    data['ports'] = ports
    data['active_page'] = 'devices'
    data['active_page_device'] = 'general'
    data['device_over_day'] = device_online_over_day
    data['device_over_week'] = device_online_over_week
    data['alerts'] = device_alerts
    data['enable_refresh'] = True
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
    ports = _sort_device_ports_by_numer(device.ports)

    scan_ports_log = ScanPorts(conn, cursor).get_by_device_id(device.id)

    data = {}
    data['device'] = device
    data['ports'] = ports
    data['scan_ports'] = scan_ports_log
    data['active_page'] = 'devices'
    data['active_page_device'] = 'ports'
    data['enable_refresh'] = True
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
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    icons = utils.device_icons()
    custom_icon = False
    if device.icon and device.icon not in icons:
        custom_icon = True

    macs = CollectDeviceMacs(conn, cursor).get_all_macs_with_device_name()

    data = {}
    data['device'] = device
    data['icons'] = icons
    data['device_types'] = utils.device_types()
    data['custom_icon'] = custom_icon
    data['all_macs'] = CollectDeviceMacs(conn, cursor).get_all_macs_with_device_name()
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


    device_notes = request.form['device_notes']
    if device_notes:
        if 'notes' not in device.metas:
            device.metas['notes'] = EntityMeta(conn, cursor)
            device.metas['notes'].create(
                meta_name='notes',
                meta_type='str',
                meta_value=device_notes)
        else:
            device.metas['notes'].value = request.form['device_notes']

    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.save()

    return redirect('/device/%s' % device.id)


@device.route('/add-mac', methods=['POST'])
@utils.authenticate
def add_mac():
    """Add a mac address to a device, by taking another devices details and combing them in to the 
       first device.

    """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = Device(conn, cursor)
    device.get_by_id(request.form['device_id'])

    device_mac = DeviceMac(conn, cursor)
    device_mac.get_by_id(request.form['device_add_mac_select'])

    original_device_mac_device_id = device_mac.device_id
    
    # Pair the mac address to the new device. 
    _pair_mac_to_device(conn, cursor, device, device_mac)

    # Finally, delete the entire device
    _delete_device(original_device_mac_device_id, conn, cursor)

    return redirect('/device/%s' % device.id)


@device.route('/delete-mac/<device_mac_id>', methods=['GET'])
@utils.authenticate
def delete_mac(device_mac_id: int):
    """Delete a macs association with a device, removing the association from the device and
       creating a new one.

    """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device_mac = DeviceMac(conn, cursor)
    device_mac.get_by_id(device_mac_id)

    # Get the original device
    og_device = Device(conn, cursor)
    og_device.get_by_id(device_mac.device_id)

    # Create a new device for the mac address being removed from the device, copying as much data as
    # possible
    device = Device(conn, cursor)
    device.name = device_mac.mac_addr
    device.ip = device_mac.ip_addr
    device.port_scan = og_device.port_scan

    device.save()

    device_mac.device_id = device.id
    device_mac.save()

    # Pair the mac address to the new device. 
    _pair_mac_to_device(conn, cursor, device, device_mac)

    return redirect('/device/%s' % og_device.id)


@device.route('/favorite/<device_id>')
@utils.authenticate
def favorite(device_id):
    """Ajax web route for making a device a favorite or not."""
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
    """Device delete. """
    _delete_device(device)

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


def _delete_device(device_id: int, conn=None, cursor=None) -> bool:
    """Delete a Device by it's id and all it's corresponding traces in the system. """
    if not conn or not cursor:
        conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return False
    device.delete()

    # Delete device witnesses
    DeviceWitnesses(conn, cursor).delete_device(device.id)
    # Delete device ports
    DevicePorts(conn, cursor).delete_device(device.id)
    # Delete device scan ports logs
    ScanPorts(conn, cursor).delete_device(device.id)
    # Delete device alerts
    Alerts(conn, cursor).delete_device(device.id)

    return True


def _pair_mac_to_device(conn, cursor, new_device: Device, device_mac: DeviceMac) -> bool:
    # Update DeviceMac
    device_mac.device_id = new_device.id
    device_mac.save()
    # Update Device Witness
    DeviceWitnesses(conn, cursor).update_device_mac_pair(new_device.id, device_mac.id)
    # Update Device Ports
    DevicePorts(conn, cursor).update_device_mac_pair(new_device.id, device_mac.id)
    # Update Device Ports
    ScanPorts(conn, cursor).update_device_mac_pair(new_device.id, device_mac.id)
    return True


def _filter_device_ports_info(device) -> list:
    """Filter device ports to a reasonable number. Prioritize ports under 1000 first, then after
       ports that have been seen within the last x period of time.
    """
    total_num_ports_to_show = 15
    hours_since_since_open_delta = int(g.options['port-open-timeout'].value)

    if len(device.ports) < total_num_ports_to_show:
        return device.ports

    time_to_incude_borring_ports = arrow.utcnow() - timedelta(hours=hours_since_since_open_delta)
    ret_ports = []

    for dp in device.ports:
        dp.get_port()

        # Include every port below 1000
        if dp.port.number < 1000:
            if dp.last_seen > time_to_incude_borring_ports:
                ret_ports.append(dp)
                continue

        # If we have less then 10 and they have been seen in 2 days include them
        if len(ret_ports) < total_num_ports_to_show:
            if dp.last_seen > time_to_incude_borring_ports:
                ret_ports.append(dp)
                continue


    # Sort the ports by their port number
    ret_ports = _sort_device_ports_by_numer(ret_ports)

    if len(ret_ports) >= total_num_ports_to_show:
        ret_ports = ret_ports[0:total_num_ports_to_show]

    return ret_ports


def _sort_device_ports_by_numer(device_ports: list) -> list:
    """Sort a list of DevicePort objects by their port number ascending. """
    ret_ports = sorted(device_ports, key = lambda i: i.port.number)
    return ret_ports



# End File: lan-nanny/lan_nanny/modules/controllers/device.py
