"""Alert - Controller

"""
from flask import Blueprint, render_template, request, jsonify
from flask import current_app as app

import arrow

from .. import db
from ..models.alert import Alert
from ..collections.alerts import Alerts


alert = Blueprint('Alert', __name__, url_prefix='/alert')


@alert.route('/')
def alerts():
    """
    Alerts roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
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
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
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


@alert.route('/alert-quick-save', methods=['POST'])
def alert_quick_save() -> str:
    """
    Ajax web route for update a device alert settings or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alert = Alert(conn, cursor)
    alert.get_by_id(request.form.get('id'))
    # import ipdb; ipdb.set_trace()

    if not alert.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Device not found')

    if request.form.get('field_name') not in ['acked', 'active']:
        print('"Forbidden field_name %s field_name"' % request.form.get('field_name'))
        return jsonify("error", "Forbidden field_name %s field_name" % request.form.get('field_name')), 403

    setattr(
        alert,
        request.form.get('field_name'),
        bool(request.form.get('field_value')))
    alert.save()

    return jsonify({"success": True})
# End File: lan-nanny/modules/controllers/alert.py
