"""Api Device Controller

"""
# import importlib
import logging
from datetime import timedelta

import arrow

from flask import Blueprint, request, jsonify, render_template, g
from flask import current_app as app

from .. import db
from .. import utils
# from .. import models
from ..models.device import Device
from ..models.device_mac import DeviceMac
from ..collections.devices import Devices
from ..models.port import Port
from ..collections.ports import Ports


api = Blueprint('Api', __name__, url_prefix='/api')
accepted_entities = ['device', 'device_mac', 'port']
accepted_collections = ['devices', 'ports']


@api.route('/info/<entity_type>/<entity_id>')
@utils.authenticate
def info(entity_type: str, entity_id: int) -> str:
    """Model info api route."""
    data = {}
    # Check if access is allowed
    if entity_type not in accepted_entities:
        data['success'] = False
        data['message'] = 'Entity info for "%s" forbidden.' % entity_type
        return jsonify(data), 403

    model = _get_model_tmp(entity_type)
    model.get_by_id(entity_id)
    if not model.id:
        return page_not_found('Device not found')

    data['success'] = True
    data['entity_type'] = entity_type
    data['object'] = model.unpack()
    return jsonify(data)


@api.route('/collect/<entity_type>')
@utils.authenticate
def collect(entity_type: str) -> str:
    """Collect model info api route."""
    data = {}
    # Check if access is allowed
    if entity_type not in accepted_collections:
        data['success'] = False
        data['message'] = 'Collections for "%s" forbidden.' % entity_type
        return jsonify(data), 403

    collect = _get_collection_tmp(entity_type)
    args = _get_args(request)
    page = _get_page_number(args)
    order_by_field = _get_order_by_field(entity_type, args)
    data['objects'] = []

    # Check for special requests.
    # Check for ids=?
    if '_get_by_ids' in args:
        objects = collect.get_by_ids(args['_get_by_ids'])

    # Gather everything else.
    else:
        collect_pages = collect.get_paginated(
            page=page,
            per_page=int(g.options['entities-per-page'].value),
            order_by={
                'field': order_by_field,
                'op': 'DESC'
            })
        objects = collect_pages['objects']

    for model in objects:
        data['objects'].append(model.unpack())

    data['success'] = True
    return jsonify(data)


@api.route('/device-connectivity/<device_id>')
@utils.authenticate
def device_connectivity(device_id: int):
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])

    # Get host scans from the last x period
    day_ago = utils.gen_sql_date((arrow.now() - timedelta(hours=2)).datetime)
    sql_hosts = """
        SELECT id, created_ts
        FROM scan_hosts
        WHERE `created_ts` >= "%s"
        ORDER BY id desc;
        """ % day_ago
    cursor.execute(sql_hosts)
    raw_host_scans = cursor.fetchall()
    sql_scan_host_ids = ""
    metric_y = []
    for scan in raw_host_scans:
        sql_scan_host_ids += "%s, " % scan[0]
        metric_y.append(scan[1])
    sql_scan_host_ids = sql_scan_host_ids[:-2]


    # Get results from those scans from device witness to see if they were there.
    sql_witness = """
        SELECT *
        FROM device_witness
        WHERE
            device_id = %s AND
            scan_id IN (%s)

    """ % (device_id, sql_scan_host_ids)
    cursor.execute(sql_witness)
    raw_device_witness = cursor.fetchall()

    device_witness_scan_ids = []
    for device_witness in raw_device_witness:
        device_witness_scan_ids.append(device_witness[5])



    print("\n\n")
    print(raw_host_scans)
    print("\n\n")

    metric = []
    metric_x = []
    for host_scan in raw_host_scans:
        print(host_scan)
        scan_instances = {
            "scan_id": host_scan[0],
            "scan_ts": host_scan[1]
        }
        if host_scan[0] in device_witness_scan_ids:
            metric_x.append(1)
            scan_instances["connected"] = 1
        else:
            metric_x.append(0)
            scan_instances["connected"] = 0

        metric.append(scan_instances)

    print("\n\n")
    print(metric)
    print("\n\n")

    # for scan_

    data = {
        'device_id': device_id,
        'day_ago': str(day_ago),
        'metric': metric,
        'metric_y': metric_y,
        'metric_x': metric_x
    }
    return jsonify(data)

# def _get_model(entity_type: str):
#     file_name = entity_type
#     model_name = entity_type
#     model_name = "%s%s" % (model_name[0].upper(), model_name[1:])
#     import_str = "..models.%s.%s" % (file_name, model_name)
#     print(model_name)
#     print(model_name)
#     print(model_name)
#     print(import_str)
#     globals()[model_name] = importlib.import_module(import_str)


def _get_model_tmp(entity_type: str):
    """Bad hack that requires each new model to be entered here... this is temporary! """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    if entity_type == 'device':
        return Device(conn, cursor)
    elif entity_type == 'device_mac':
        return DeviceMac(conn, cursor)
    elif entity_type == 'port':
        return Port(conn, cursor)
    else:
        logging.error('Unknown model: %s' % entity_type)


def _get_collection_tmp(entity_type: str):
    """Bad hack that requires each new collection model to be entered here... this is temporary! """
    conn, cursor = db.connect_mysql(app.config['LAN_NANNY_DB'])
    if entity_type == 'devices':
        return Devices(conn, cursor)
    elif entity_type == 'ports':
        return Ports(conn, cursor)
    else:
        logging.error('Unknown model: %s' % entity_type)


def _get_args(request_data: dict) -> dict:
    """Parse the request args into a dict. """
    args = {}
    for key, value in request.args.items():
        if key == 'ids':
            if ',' in value:
                _ids = value.split(',')
            else:
                _ids = [value]
            args['_get_by_ids'] = _ids
        else:
            args[key] = value
    return args


def _get_page_number(args: dict) -> int:
    """Get a collection page number from the parsed request arguments. """
    if 'page' in args:
        return args['page']
    else:
        return 1


def _get_order_by_field(entity_type, args) -> str:
    if entity_type == 'devices':
        return 'last_seen'
    else:
        return 'created_ts'


def page_not_found(e: str):
    """404 Error page."""
    return render_template('errors/404.html', error=e), 404


# End File: lan-nanny/lan_nanny/modules/controllers/api_device.py
