"""Api Devices -  Controller
Handles web routes for Devices
/api/devices/

"""
import arrow

from flask import Blueprint, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.devices import Devices as DevicesCollect
from ..models.device import Device as DeviceModel

api_devices = Blueprint('ApiDevices', __name__, url_prefix='/api/devices')


@api_devices.route('/')
@utils.authenticate
def index() -> str:
    """Devices roster."""
    page = 1

    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    device_collection = DevicesCollect(conn, cursor)
    device_pages = device_collection.get_paginated(
        page=page,
        order_by={
            'field': 'last_seen',
            'op' : 'DESC'
        })

    objects = device_collection.unpack_models(device_pages['objects'])
    data = {
        'pages': device_pages['info'],
        'objects': objects,
    }
    return jsonify(data)


# End File: lan-nanny/lan_nanny/modules/controllers/api_devices.py
