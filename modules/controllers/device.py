"""Device - Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify

from .. import db
from .. import utils
from ..collections.devices import Devices
from ..models.alert import Alert
from ..models.device import Device
from ..models.witness import Witness

device = Blueprint('Device', __name__, url_prefix='/device')
DATABASE = "../../lan_nanny.db"


@device.route('/')
def devices() -> str:
    """
    Devices roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    devices = Devices(conn, cursor)
    data = {}
    data['active_page'] = 'devices'
    data['devices'] = devices.get_all()
    return render_template('devices/roster.html', **data)


@device.route('/info/<device_id>')
def info(device_id: int) -> str:
    """
    Device info page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    data = {}
    data['device'] = device
    data['active_page'] = 'devices'
    return render_template('devices/info.html', **data)


@device.route('/edit/<device_id>')
def edit(device_id: int) -> str:
    """
    Device edit page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
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
    data['custom_icon'] = custom_icon
    data['active_page'] = 'devices'
    return render_template('devices/edit.html', **data)


@device.route('/save', methods=['POST'])
def save():
    """
    Device save.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
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

    if request.form.get('device_port_scan'):
        device.port_scan = 1
    else:
        device.port_scan = 0

    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.save()

    return redirect('/device/info/%s' % device.id)


@device.route('/favorite/<device_id>')
def favorite(device_id):
    """
    Web route for making a device a favorite or not.

    """
    conn, cursor = db.get_db_flask(DATABASE)
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


@device.route('/alert/<device_id>/<alert_type>/<alert_value>')
def alert(device_id: int, alert_type: str, alert_value: int) -> str:
    """
    Web route for making a device alert or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)
    if not device.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    if alert_type == "online":
        device.alert_online = alert_value
    elif alert_type == "offline":
        device.alert_offline = alert_value
    else:
        return jsonify({"success": False, "error": "Alert type is in correct."})

    device.save()

    return jsonify({"success": True})


@device.route('/delete/<device_id>')
def delete(device_id: int):
    """
    Device delete.

    """
    conn, cursor = db.get_db_flask(DATABASE)

    # Delete the device
    device = Device(conn, cursor)
    device.get_by_id(device_id)
    device.delete()

    # Delete devices witness
    witness = Witness(conn, cursor)
    witness.delete_device(device.id)

    # Delete device alerts
    alert = Alert(conn, cursor)
    alert.delete_device(device.id)

    return redirect('/device')

# End File: lan-nanny/modules/controllers/device.py
