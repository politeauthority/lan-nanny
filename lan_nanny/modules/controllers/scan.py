"""Scan - Controller

"""
from flask import Blueprint, render_template
from flask import current_app as app

from .. import db
from ..models.run_log import RunLog
from ..collections.run_logs import RunLogs

scan = Blueprint('Scan', __name__, url_prefix='/scan')


@scan.route('/')
def roster():
    """
    Scans roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    run_logs = RunLogs(conn, cursor)
    data = {
        'active_page': 'scans',
        'scans': run_logs.get_all()
    }
    return render_template('scans/roster.html', **data)


@scan.route('/info/<scan_id>')
def info(scan_id):
    """
    Scan info page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    run_log = RunLog(conn, cursor)
    scan = run_log.get_by_id(scan_id)
    if not scan.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Scan not found')
    data = {}
    data['active_page'] = 'scans'
    data['scan'] = scan

    return render_template('scans/info.html', **data)

# End File: lan-nanny/modules/controllers/scan.py
