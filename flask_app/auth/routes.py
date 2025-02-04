from flask import Blueprint
from flask import request
from flask import redirect
from functools import wraps
from typing import Callable
from flask_app.auth.services import check_login
from flask_app.auth.services import check_admin
from flask_app.auth.services import try_login
from flask_app.auth.services import logout as logout_s
from flask_app.auth.services import create_user
from flask_app.auth.services import check_unique_register_input
from flask_app.auth.services import get_profile
from flask_app.auth.views import not_logged_in_view
from flask_app.auth.views import not_admin_view
from flask_app.auth.views import auth_view


from flask_app.views import json_result

bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_page(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return redirect('/') # change to redirect to flask_app.routes.home
        return f(*args, **kwargs)
    return decorated_function

def admin_endpoint(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return not_admin_view()
        return f(*args, **kwargs)
    return decorated_function

def login_required_page(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return redirect('/') # change to redirect to flask_app.routes.home
        return f(*args, **kwargs)
    return decorated_function

def login_required_endpoint(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return not_logged_in_view()
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET'])
def login():
    return auth_view('login')

@bp.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()['formData']
    result = try_login(data)
    return json_result(result)

@bp.route('/logout', methods=['GET'])
def logout():
    logout_s()
    return redirect('/') # change to redirect to flask_app.routes.home

@bp.route('/register', methods=['GET'])
def register():
    return auth_view('register')

@bp.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()
    result = create_user(data)
    return json_result(result)

@bp.route('/unique_username', methods=['POST'])
def unique_username():
    data = request.get_json()
    result = check_unique_register_input('username', data)
    return json_result(result)

@bp.route('/unique_email', methods=['POST'])
def unique_email():
    data = request.get_json()
    result = check_unique_register_input('email', data)
    return json_result(result)

@bp.route('/profile', methods=['GET'])
@login_required_endpoint
def profile():
    result = get_profile()
    return json_result(result)