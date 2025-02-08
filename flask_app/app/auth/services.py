from flask import session
from app.data_access.models import Func_Result
from app.auth.data_access.models import New_User

from app.auth.data_access.db import AuthDB
from app.data_access import RD
import bcrypt
import threading

DB = AuthDB()

def create_user(data: dict[str, str]) -> Func_Result:
    new_user = New_User(data['first_name'], data['last_name'], data['username'], data['email'], data['password'])
    register = DB.create_user(new_user)
    if not register.success:
        session['logged_in'] = False
        session['user_id'] = None
        return Func_Result(False, None)
    session['logged_in'] = True
    session['user_id'] = register.result
    return Func_Result(True, {'registered': True})

def try_login(data: dict[str, str]) -> Func_Result:
    username = data['username']
    password = data['password']
    check_user = DB.check_user(username)
    if not check_user.success:
        return Func_Result(False, None)
    if check_user.result:
        user_id, hashed_password, is_admin = check_user.result
        if bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hashed_password)):
            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = is_admin
            return Func_Result(True, {'logged_in': True})
    return Func_Result(True, {'logged_in': False})

def logout() -> None:
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

def get_profile() -> Func_Result:
    user_id = session['user_id']
    try:
        profile = DB.get_profile(user_id)
        return Func_Result(True, profile)
    except Exception as e:
        print('Error getting profile')
        return Func_Result(False, {'error': 'Error getting profile', 'message': str(e)})
