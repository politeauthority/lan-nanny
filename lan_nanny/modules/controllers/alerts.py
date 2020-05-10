"""Alert - Controller

"""
from flask import Blueprint, render_template, request, redirect, jsonify
from flask import current_app as app

import arrow

from .. import db
from .. import utils
from ..models.alert import Alert
from ..models.entity_meta import EntityMeta
from ..models.device import Device
from ..collections.alerts import Alerts as AlertsCollect
from ..collections.devices import Devices as DevicesCollect

alerts = Blueprint('Alert', __name__, url_prefix='/alerts')


@alerts.route('/')
@utils.authenticate
def dashboard():
    """Alerts dashboard page."""
    # Send everything to all, theres no good dashboard now
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    alerts_collect = AlertsCollect(conn, cursor)
    alerts_firing = alerts_collect.get_firing()
    alerts_unacked_resolved = alerts_collect.get_unacked_resolved()

    device_alerts = alerts_firing + alerts_unacked_resolved
    devices = get_alert_devices(conn, cursor, device_alerts)
    data = {}
    data['alerts_num_today'] = alerts_collect.get_count_since(86400)
    data['alerts_firing'] = alerts_firing
    data['alerts_unacked_resolved'] = alerts_unacked_resolved
    data['alerts_recent'] = alerts_collect.get_recent()
    data['devices'] = devices
    data['active_page'] = 'alerts'
    data['active_page_alerts'] = 'dashboard'
    return render_template('alerts/dashboard.html', **data)


@alerts.route('/all')
@alerts.route('/all/<page>')
@utils.authenticate
def roster(page: str="1") -> str:
    """Alerts roster page."""
    page = int(page)
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    alert_collect = AlertsCollect(conn, cursor)
    alert_pages = alert_collect.get_paginated(
        page=page,
        order_by={
            'field': 'created_ts',
            'op' : 'DESC'
        })

    # Get alert metas
    for alert_obj in alert_pages['objects']:
        alert_obj.get_meta()

    devices = get_alert_devices(conn, cursor, alert_pages['objects'])

    data = {}
    data['alerts'] = alert_pages['objects']
    data['pagination'] = utils.gen_pagination_urls('/alerts/all/', alert_pages['info'])
    data['devices'] = devices
    data['active_page'] = 'alerts'
    data['active_page_alerts'] = 'all'
    return render_template('alerts/roster.html', **data)


@alerts.route('/info/<alert_id>')
@utils.authenticate
def info(alert_id: int):
    """Alert info page."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id)
    if not alert.id:
        return 'ERROR 404: Route this to page_not_found method!', 404
        # return page_not_found('Alert not found')

    # hitting the alert info is considered acking the alert.
    if not alert.acked:
        alert.acked = True
        alert.acked_ts = arrow.utcnow().datetime
        alert.save()

    device = None
    if alert.kind in ['new-device', 'device-offline']:
        device = Device(conn, cursor)
        device.get_by_id(int(alert.metas['device'].value))
    data = {}
    data['alert'] = alert
    data['device'] = device
    data['active_page'] = 'alerts'
    return render_template('alerts/info.html', **data)


@alerts.route('/alert-quick-save', methods=['POST'])
@utils.authenticate
def alert_quick_save() -> str:
    """Ajax web route for update a device alert settings or not when coming on or off the
       network.
    """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
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
@utils.authenticate
def delete(alert_id: int):
    """Alert delete."""
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    alert = Alert(conn, cursor)
    alert.get_by_id(alert_id)
    alert.delete()
    return redirect('/alerts')


def get_alert_devices(conn, cursor, alerts):
    # Get alert devices
    alert_device_ids = []
    for alert_obj in alerts:
        if 'device' in alert_obj.metas:
            device_id = int(alert_obj.metas['device'].value)
            if device_id not in alert_device_ids:
                alert_device_ids.append(device_id)
    devices = {}
    if alert_device_ids:
        device_collect = DevicesCollect(conn, cursor)
        devices = device_collect.get_by_ids_keyed(alert_device_ids)
    return devices

# End File: lan-nanny/lan_nanny/modules/controllers/alerts.py
