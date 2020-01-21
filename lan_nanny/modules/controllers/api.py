"""API Controller

"""
from datetime import timedelta

import arrow

from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.scan_logs import ScanLogs

api = Blueprint('Api', __name__, url_prefix='/api')


@api.route('/device_online/<device_id>')
@utils.authenticate
def device_online(device_id) -> str:
    """Device online"""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    host_scans = ScanLogs(conn, cursor).get_host_scans_24_hours()

    return jsonify(host_scans)



# End File: lan-nanny/lan_nanny/modules/controllers/api.py
