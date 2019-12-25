import sqlite3
import sys

from modules.device import Device
from modules.devices import Devices
from modules import filters

from flask import Flask, redirect, render_template, request, g


DATABASE = "lan_nanny.db"
app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db, db.cursor()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index() -> str:
    """
    App home page.

    """
    conn, cursor = get_db()
    devices = Devices()
    devices.conn = conn
    devices.cursor = cursor
    data = {}
    data['devices'] = devices.get_all()
    return render_template('index.html', **data)


@app.route('/device/<device_id>')
def device(device_id: int) -> str:
    """
    Device info page.

    """
    conn, cursor = get_db()
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    data = {}
    data['device'] = device
    print(data)
    return render_template('device.html', **data)

@app.route('/device-edit/<device_id>')
def device_edit(device_id: int) -> str:
    """
    Device info page.

    """
    conn, cursor = get_db()
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(device_id)

    data = {}
    data['device'] = device
    return render_template('device_edit.html', **data)

@app.route('/device-save', methods=['POST'])
def device_save() -> str:
    """
    Device info page.

    """
    conn, cursor = get_db()
    device = Device()
    device.conn = conn
    device.cursor = cursor
    device.get_by_id(request.form['device_id'])

    device.name = request.form['device_name']
    device.vendor = request.form['device_vendor']
    # @todo figure out how hide works.
    # device.hide = request.form['device_hide']
    device.icon = request.form['device_icon']
    device.update()

    return redirect('/device/%s' % device.id)

@app.route('/settings')
def settings() -> str:
    """
    Settings page.

    """
    return render_template('settings.html')


def register_jinja_funcs(app):
    """
    Makes functions avialble to jinja templates.
    """
    app.jinja_env.filters['last_seen'] = filters.last_seen

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]

    register_jinja_funcs(app)
    app.run(host="0.0.0.0", port=port)


# End File: lan-nanny/app.py
