"""Api Device Controller

"""
# import importlib
import logging

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
