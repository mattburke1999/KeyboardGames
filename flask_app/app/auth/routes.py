from flask import Blueprint
from flask import request
from functools import wraps
from typing import Callable
from app.auth.services import check_login
from app.auth.services import check_admin
from app.auth.services import try_login
from app.auth.services import logout_process
from app.auth.services import create_user
from app.auth.services import check_unique_register_input
from app.auth.services import get_profile
from app.auth.views import not_logged_in_view
from app.auth.views import not_admin_view
from app.auth.views import not_localhost_view
from app.auth.views import auth_view
from app.views import json_result

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

def admin_only(type: str):
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_admin():
                return not_admin_view(type)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(type: str):
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_login():
                return not_logged_in_view(type)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def localhost_only(type: str):
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
                return not_localhost_view(type)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/login', methods=['GET'])
def login():
    return auth_view('login')

@bp.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    result = try_login(data)
    return json_result(result)

@bp.route('/logout', methods=['GET'])
def logout():
    logout_process()
    return not_logged_in_view('page')

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
@login_required('api')
def profile():
    result = get_profile()
    return json_result(result)