"""Alert - Controller

"""
from flask import Blueprint, render_template

import arrow

from .. import db
from ..models.alert import Alert
from ..collections.alerts import Alerts


alert = Blueprint('Alert', __name__, url_prefix='/alert')

DATABASE = "../../lan_nanny.db"


@alert.route('/')
def alerts():
    """
    Alerts roster page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alerts = Alerts(conn, cursor)
    data = {}
    data['alerts'] = alerts.get_all()
    data['active_page'] = 'alerts'
    return render_template('alerts/roster.html', **data)


@alert.route('/info/<alert_id>')
def alert_info(alert_id: int):
    """
    Alert info page.

    """
    conn, cursor = db.get_db_flask(DATABASE)
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id, build_device=True)
    if not alert.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Alert not found')

    if not alert.acked:
        alert.acked = 1
        alert.acked_ts = arrow.utcnow().datetime
        alert.save()
    data = {}
    data['active_page'] = 'alert-info'
    data['alert'] = alert
    data['active_page'] = 'alerts'
    return render_template('alerts/info.html', **data)

# End File: lan-nanny/modules/controllers/alert.py
