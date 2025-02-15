from flask import Blueprint
from flask import request
from app.auth.services import try_login
from app.auth.services import logout_process
from app.auth.services import create_user
from app.auth.services import check_unique_register_input
from app.auth.views import not_logged_in_view
from app.auth.views import auth_view
from app.views import json_result
from app.utils.route_decorators import require_json

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

@bp.route('/login', methods=['GET'])
def login():
    return auth_view('login')

@bp.route('/login', methods=['POST'])
@require_json
def login_post(data):
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
@require_json
def register_post(data):
    result = create_user(data)
    return json_result(result)

@bp.route('/unique_username', methods=['POST'])
@require_json
def unique_username(data):
    result = check_unique_register_input('username', data)
    return json_result(result)

@bp.route('/unique_email', methods=['POST'])
@require_json
def unique_email(data):
    result = check_unique_register_input('email', data)
    return json_result(result)

