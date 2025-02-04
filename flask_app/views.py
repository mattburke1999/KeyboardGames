from flask import render_template
from flask import redirect
from flask import jsonify
from services import get_home_page_data
from services import check_unique_register_input
from services import create_user
from services import try_login
from services import logout
from services import get_profile
from services import check_login
from services import check_admin
from functools import wraps
from typing import Callable
from models import New_User
from models import Func_Result

def admin_page(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def admin_endpoint(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return json_result(Func_Result(False, {'is_admin': False, 'message': 'You must be an admin to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def login_required_page(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def login_required_endpoint(f: Callable):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return json_result(Func_Result(False, {'logged_in': False, 'message': 'You must be logged in to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def json_result(result: Func_Result):
    if result.success:
        return (jsonify(result.result), 200) 
    else:
        if result.result and 'logged_in' in result.result and not result.result['logged_in']:
            return (jsonify(result.result), 401)
        return (jsonify(result.result), 500)

# page
def home_view():
    home_page = get_home_page_data()
    if not home_page.success or not home_page.result:
        return render_template('505.html'), 505
    return render_template('index.html', home_page=home_page.result)

# page
def auth_view(page: str):
    return render_template('login.html', page=page)

# endpoint
def check_unique_register_input_view(type: str, value: str):
    result = check_unique_register_input(type, value)
    return json_result(result)

# endpoint
def register_view(new_user: New_User):
    result = create_user(new_user)
    return json_result(result)

# endpoint
def login_view(username: str, password: str):
    result = try_login(username, password)
    return json_result(result)

# endpoint
def logout_view():
    logout()
    return redirect('/')

# endpoint
def profile_view():
    result = get_profile()
    return json_result(result)