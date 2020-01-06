"""Device Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.devices import Devices
from ..collections.ports import Ports
from ..models.alert import Alert
from ..models.device import Device
from ..models.witness import Witness

port = Blueprint('Port', __name__, url_prefix='/port')


@port.route('/')
def roster() -> str:
    """
    Devices roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    ports = Ports(conn, cursor)
    data = {}
    data['active_page'] = 'ports'
    data['ports'] = ports.get_distinct()
    return render_template('ports/roster.html', **data)


# End File: lan-nanny/lan_nanny/modules/controllers/ports.py
