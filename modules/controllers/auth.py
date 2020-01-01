"""Authenticate - Controller
"""
from flask import Blueprint, request, redirect, session

from app.utilities import auth
from app.utilities import common

authenticate = Blueprint('Authenticate', __name__, url_prefix='/auth')


@authenticate.route('', methods=['POST'])
def index():
    """
    /*
    Index
    Runs the authentication and redirections
    @todo make more flexable urls.
    """
    if not request.form.get('username') or not request.form.get('password'):
        return redirect('/failed-login', 403)

    if auth.check():
        return redirect(common.admin_uri())

    login = auth.login(request.form['username'], request.form['password'])
    if not login:
        return redirect('/failed-login', 403)

    return redirect(common.admin_uri())


@authenticate.route('/logout')
def logout():
    """
    /auth/logout
    Logs out the user by destroying the session
    """
    if session.get('username'):
        session.pop('username')
    if session.get('authenticated'):
        session.pop('authenticated')
    return redirect(common.admin_uri())


def flask_admin_auth():
    """
    Interface for FlaskAdmin's auth style.
    Basically, if we're logged in, and hititng this method, we're trying to logout, else try and authenticate.
    """
    if session.get('authenticated'):
        return logout()
    else:
        return index()


# End File: simple-honey/app/controllers/authenticate.py
