from flask import session
from .data_access.models import New_User
from .data_access.db import AuthDB
from app.data_access import RD
from app.data_access.models import Func_Result
import bcrypt
import traceback
import threading
from typing import Literal

DB = AuthDB()

def parse_user_data_and_validate(data: dict[str, str]) -> New_User | None:
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    username = data.get('username', None)
    email = data.get('email', None)
    password = data.get('password', None)
    if not first_name or not last_name or not username or not email or not password:
        return None
    new_user = New_User(first_name, last_name, username, email, password)
    return new_user

def create_user(data: dict[str, str]) -> Func_Result:
    new_user = parse_user_data_and_validate(data)
    if not new_user:
        return Func_Result(True, {'registered': False, 'error': 'Missing required fields'})
    conn = None
    try:
        with DB.connect_db() as conn:
            new_user_id = DB.create_user(conn, new_user)
            if not new_user_id:
                raise Exception('Error creating user')
            DB.add_default_skin(conn, new_user_id)
            conn.commit()
            session['logged_in'] = True
            session['user_id'] = new_user_id
            return Func_Result(True, {'registered': True})
    except Exception:
        e = traceback.format_exc()
        if conn:
            conn.rollback()
        session['logged_in'] = False
        session['user_id'] = None
        return Func_Result(False, {'error': str(e)})

def try_login(data: dict[str, str]) -> Func_Result:
    username = data.get('username', None)
    password = data.get('password', None)
    if not username or not password:
        return Func_Result(True, {'error': 'Missing username or password'})
    try:
        user_id, hashed_password, is_admin = DB.check_user(username)
        if user_id and bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hashed_password)): # type: ignore
            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = is_admin or False
            return Func_Result(True, {'logged_in': True})
        return Func_Result(True, {'logged_in': False})
    except Exception:
        e = traceback.format_exc()
        return Func_Result(False, {'error': str(e)})

def logout_process() -> None:
    session.clear()
    # create a thread to clear user sessions in the background so this returns immediately
    threading.Thread(target=RD.clear_user_sessions, args=(session['user_id'],)).start()
    
def check_login() -> bool:
    return 'logged_in' in session and session['logged_in'] and 'user_id' in session and session['user_id']

def check_admin() -> bool:
    return 'is_admin' in session and session['is_admin']

def check_unique_register_input(input_type: Literal['username', 'email'], data: dict[str, str]) -> Func_Result:
    if input_type not in {'username', 'email'}:
            return Func_Result(True, {'error': 'Invalid input type'})
    input = data.get(input_type, None)
    if not input:
        return Func_Result(True, {'error': 'Missing input'})
    try:
        unique_check = DB.check_unique_register_input(input_type, input)
        return Func_Result(True, {'unique': unique_check})
    except Exception as e:
        return Func_Result(False, {'error': str(e)})

