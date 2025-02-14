from flask import session
from .data_access.models import New_User
from .data_access.db import AuthDB
from app.data_access import RD
from app.data_access.models import Func_Result
import bcrypt
import traceback
import threading

DB = AuthDB()

def create_user(data: dict[str, str]) -> Func_Result:
    new_user = New_User(data['first_name'], data['last_name'], data['username'], data['email'], data['password'])
    with DB.connect_db() as conn:
        try:
            new_user_id = DB.create_user(conn, new_user)
            if not new_user_id:
                raise Exception('Error creating user')
            DB.add_default_skin(conn, new_user_id)
            conn.commit()
            session['logged_in'] = True
            session['user_id'] = new_user_id
            return Func_Result(True, {'registered': True})
        except Exception as e:
            conn.rollback()
            session['logged_in'] = False
            session['user_id'] = None
            return Func_Result(False, {'error': str(e)})

def try_login(data: dict[str, str]) -> Func_Result:
    username = data['username']
    password = data['password']
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

def check_unique_register_input(input_type: str, data: dict[str, str]) -> Func_Result:
    try:
        unique_check = DB.check_unique_register_input(input_type, data[input_type])
        return Func_Result(True, {'unique': unique_check})
    except Exception as e:
        return Func_Result(False, {'error': str(e)})

