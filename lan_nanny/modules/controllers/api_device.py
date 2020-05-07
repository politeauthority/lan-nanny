"""Api Device -  Controller
Handles web routes for a single device
/api/device/

"""
from flask import Blueprint, jsonify
from flask import current_app as app

from .. import db
from .. import utils
from ..models.device import Device as DeviceModel
from ..collections.device_witnesses import DeviceWitnesses

api_device = Blueprint('ApiDevice', __name__, url_prefix='/api/device')


@api_device.route('/<device_id>')
@utils.authenticate
def index(device_id) -> str:
    """Device details."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = DeviceModel(conn, cursor)
    device.get_by_id(device_id)

    data = {
        'object': device.unpack_model(),
    }
    return jsonify(data)


@api_device.route('/<device_id>/witness')
@api_device.route('/<device_id>/witness/<timeframe>')
@utils.authenticate
def witness(device_id, timeframe=86400) -> str:
    """Device witness details."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device = DeviceModel(conn, cursor)
    device.get_by_id(device_id)

    collect_witness = DeviceWitnesses(conn, cursor)
    device_witness = collect_witness.get_device_since(device.id, timeframe)

    data = {
        'device': device.unpack_model(),
        'objects': device_witness,
    }
    return jsonify(data)


# End File: lan-nanny/lan_nanny/modules/controllers/api_device.py
