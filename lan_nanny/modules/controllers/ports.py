"""Ports Controller

"""
from flask import Blueprint, render_template, g
from flask import current_app as app

from .. import db
from .. import utils
from ..models.port import Port as PortModel
from ..collections.ports import Ports as PortsCollect
from ..collections.devices import Devices

ports = Blueprint('Port', __name__, url_prefix='/ports')


@ports.route('/')
@utils.authenticate
def dashboard() -> str:
    """Port roster page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    ports_collect = PortsCollect(conn, cursor)
    devices = Devices(conn, cursor).with_enabled_port_scanning()
    data = {}
    data['active_page_ports'] = 'ports'
    data['ports'] = ports_collect.get_privileged()
    data['devices'] = devices
    data['ports_total'] = ports_collect.get_count_total()
    data['active_page'] = 'ports'
    data['active_page_ports'] = 'dashboard'
    data['enable_refresh'] = True
    return render_template('ports/dashboard.html', **data)


@ports.route('/all')
@ports.route('/all/<page>')
@utils.authenticate
def roster(page: str="1") -> str:
    """Port roster pages."""
    page = int(page)
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    ports_collect = PortsCollect(conn, cursor)
    port_pages = ports_collect.get_paginated(
        page=page,
        per_page=int(g.options['entities-per-page'].value),
        order_by={
            'field': 'number',
            'op': 'ASC'
        })
    data = {}
    data['ports'] = port_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/ports/all/', port_pages['info'])
    data['ports_total'] = ports_collect.get_count_total()
    data['active_page'] = 'ports'
    data['active_page_ports'] = 'all'
    data['enable_refresh'] = True
    return render_template('ports/roster.html', **data)


@ports.route('/info/<port_id>')
@utils.authenticate
def info(port_id: int) -> str:
    """Port info page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    port = PortModel(conn, cursor)
    port.get_by_id(port_id)

    if not port.id:
        return 'ERROR 404: Route this to page_not_found method!', 404

    device_collect = Devices(conn, cursor)
    devices = device_collect.get_with_open_port(port.id)
    data = {}
    data['port'] = port
    data['devices'] = devices
    data['active_page'] = 'ports'
    data['active_page_ports'] = 'info'
    data['enable_refresh'] = True
    return render_template('ports/info.html', **data)

# End File: lan-nanny/lan_nanny/modules/controllers/ports.py
