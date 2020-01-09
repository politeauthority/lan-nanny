"""Ports Controller

"""
from flask import Blueprint, render_template, redirect, request, jsonify, g
from flask import current_app as app

from .. import db
from .. import utils
from ..collections.ports import Ports

ports = Blueprint('Port', __name__, url_prefix='/ports')


@ports.route('/')
def roster() -> str:
    """
    Port roster page.

    """
    conn, cursor = db.get_db_flask(app.config['LAN_NANNY_DB_FILE'])
    ports = Ports(conn, cursor)
    data = {}
    data['active_page'] = 'ports'
    data['ports'] = ports.get_distinct()
    return render_template('ports/roster.html', **data)


# End File: lan-nanny/lan_nanny/modules/controllers/ports.py
