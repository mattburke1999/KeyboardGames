
from flask import request
from functools import wraps
from typing import Callable
from app.auth.services import check_login
from app.auth.services import check_admin
from app.auth.views import not_logged_in_view
from app.auth.views import not_admin_view
from app.auth.views import not_localhost_view
from app.views import invalid_request_format_view

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

def require_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if not isinstance(data, dict):
            return invalid_request_format_view()
        return f(data, *args, **kwargs)
    return decorated_function

def get_client_ip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(request.remote_addr, *args, **kwargs)
    return decorated_function