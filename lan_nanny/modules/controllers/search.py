"""Ports Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.devices import Devices
from ..collections.ports import Ports

search = Blueprint('Search', __name__, url_prefix='/search')


@search.route('/results', methods=['POST'])
def results() -> str:
    """
    Port roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    search_phrase = request.form['search'].strip()
    devices = Devices(conn, cursor)
    found_devices = devices.search(search_phrase)

    ports = Ports(conn, cursor)
    found_ports = ports.search(search_phrase)

    total = len(found_devices) + len(found_ports)
    data = {}
    data['search_phrase'] = search_phrase
    data['total_results'] = total
    data['devices'] = found_devices
    data['ports'] = found_ports
    return render_template('search/results.html', **data)


# End File: lan-nanny/lan_nanny/modules/controllers/search.py
