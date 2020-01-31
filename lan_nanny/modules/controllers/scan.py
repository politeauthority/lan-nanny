"""Scan - Controller

"""
from flask import Blueprint, render_template
from flask import current_app as app

from .. import db
from .. import utils
from ..models.scan_log import ScanLog
from ..collections.scan_logs import ScanLogs
from ..collections.witnesses import Witnesses

scan = Blueprint('Scan', __name__, url_prefix='/scan')


@scan.route('/')
@utils.authenticate
def roster():
    """
    Scans roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan_logs = ScanLogs(conn, cursor)
    data = {
        'active_page': 'scans',
        'scans': scan_logs.get_all()
    }
    return render_template('scans/roster.html', **data)


@scan.route('/info/<scan_id>')
@utils.authenticate
def info(scan_id):
    """
    Scan info page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    scan = ScanLog(conn, cursor)
    scan.get_by_id(scan_id)
    if not scan.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Scan not found')

    witnesses = Witnesses(conn, cursor).get_by_scan_id(scan.id)
    data = {}
    data['active_page'] = 'scans'
    data['scan'] = scan
    data['witnesses'] = witnesses
    return render_template('scans/info.html', **data)

# End File: lan-nanny/modules/controllers/scan.py
