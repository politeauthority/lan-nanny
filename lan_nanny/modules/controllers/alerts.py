"""Alert - Controller

"""
from flask import Blueprint, render_template, request, redirect, jsonify
from flask import current_app as app

import arrow

from .. import db
from .. import utils
from ..models.alert import Alert
from ..collections.alerts import Alerts
from ..collections.devices import Devices


alerts = Blueprint('Alert', __name__, url_prefix='/alerts')


@alerts.route('/')
@utils.authenticate
def dashboard():
    """Alerts dashboard page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alerts = Alerts(conn, cursor)
    data = {}
    data['alerts'] = alerts.get_all()
    data['active_page'] = 'alerts'
    data['active_page_alerts'] = 'dashboard'
    return render_template('alerts/dashboard.html', **data)


@alerts.route('/all')
@utils.authenticate
def roster():
    """Alerts roster page."""
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alerts = Alerts(conn, cursor)
    data = {}
    data['alerts'] = alerts.get_all()
    data['active_page'] = 'alerts'
    data['active_page_alerts'] = 'dashboard'
    return render_template('alerts/roster.html', **data)


@alerts.route('/info/<alert_id>')
def info(alert_id: int):
    """
    Alert info page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id, build_device=True, build_alert_events=True)
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


@alerts.route('/alert-quick-save', methods=['POST'])
def alert_quick_save() -> str:
    """
    Ajax web route for update a device alert settings or not when coming on or off the network.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    alert = Alert(conn, cursor)
    alert.get_by_id(request.form.get('id'))

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

@alerts.route('/delete/<alert_id>')
def delete(alert_id: int):
    """
    Alert delete.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])

    # Delete the device
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id)
    alert.delete()
    alert.delete_alert_events()

    return redirect('/alert')

# End File: lan-nanny/lan_nanny/modules/controllers/alerts.py