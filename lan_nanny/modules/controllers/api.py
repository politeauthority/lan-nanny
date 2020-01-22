"""API Controller

"""
from datetime import timedelta

import arrow

from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.scan_logs import ScanLogs
from ..models.scan_log import ScanLog


api = Blueprint('Api', __name__, url_prefix='/api')


@api.route('/device-online/<device_id>')
@utils.authenticate
def device_online(device_id) -> str:
    """Device online"""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    host_scans = get_host_scans_24_hours(conn, cursor, device_id)
    formatted_data = format_data(host_scans, device_id)

    data = {
        'data': formatted_data
    }
    return jsonify(data)


def get_host_scans_24_hours(conn, cursor, device_id):
    """Get all host scans from the last 24 hours

    """
    hours_24 = arrow.utcnow().datetime - timedelta(hours=24)
    sql = """
        SELECT scan_logs.id, scan_logs.created_ts, witness.device_id
        FROM scan_logs
            LEFT OUTER JOIN witness
                ON
                    scan_logs.id = witness.scan_id AND
                    witness.device_id = %s
        WHERE
            scan_type = "host" AND
            trigger = "cron" AND
            scan_logs.created_ts >= "%s"
            ORDER BY scan_logs.created_ts DESC;
            """ % (device_id, hours_24)

    print("\n\n")
    print(sql)
    print("\n\n")
    cursor.execute(sql)
    raw_scans = cursor.fetchall()
    # scan_logs = []
    # for raw_scan in raw_scans:
    #     scan = ScanLog(conn, cursor)
    #     scan.build_from_list(raw_scan)
    #     scan_logs.append(scan)
    return raw_scans

def format_data(host_scans, device_id):
    data = []
    for scan in host_scans:
        point = {}
        point['scan_id'] = scan[0]
        point['start'] = scan[1]
        point['device_id'] = int(device_id)
        point['online_int'] = 0
        point['online'] = False
        if scan[2] == int(device_id):
            point['online'] = True
            point['online_int'] = 1
        data.append(point)

    return data


# End File: lan-nanny/lan_nanny/modules/controllers/api.py
