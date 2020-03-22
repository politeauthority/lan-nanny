"""Ports Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..models.port import Port
from ..collections.ports import Ports
from ..collections.devices import Devices

ports = Blueprint('Port', __name__, url_prefix='/ports')


@ports.route('/')
@utils.authenticate
def roster() -> str:
    """Port roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    ports = Ports(conn, cursor)
    devices = Devices(conn, cursor).with_enabled_port_scanning()
    data = {}
    data['active_page'] = 'ports'
    data['ports'] = ports.get_all()
    data['devices'] = devices
    return render_template('ports/roster.html', **data)


@ports.route('/info/<port_number>/<port_protocol>')
@utils.authenticate
def info(port_number: str, port_protocol: str) -> str:
    """Port info page."""
    print('PORT INFO\n\n')
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    port = Port(conn, cursor)
    port.get_by_port_and_protocol(port_number, port_protocol)

    if not port.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    device_collect = Devices(conn, cursor)
    devices = device_collect.get_with_open_port(port.id)
    data = {}
    data['port'] = port
    data['devices'] = devices
    data['active_page'] = 'ports'
    return render_template('ports/info.html', **data)

# End File: lan-nanny/lan_nanny/modules/controllers/ports.py
