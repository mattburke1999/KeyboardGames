from models import Func_Result
from models import Home_Page
from db import check_unique_register_input as db_check_unique_register_input
from db import create_user as db_create_user
from models import New_User
from db import check_user as db_check_user
from db import get_profile as db_get_profile
from models import Profile
from redis_store import clear_user_sessions as rd_clear_user_sessions
from flask import session
import bcrypt
import threading
import socket

from flask_app.games.services import get_games

GAME_INFO = {}
GAMES = []

def get_home_page_data() -> Func_Result:
    games = get_games()
    if not games.success or not games.result:
        return Func_Result(False, None)
    logged_in = check_login()
    print(f'service logged_in: {logged_in}')
    return Func_Result(True, Home_Page(games.result[1], games.result[0], logged_in))

def create_user(new_user: New_User) -> Func_Result:
    # first_name, last_name, username, email, password):
    register = db_create_user(new_user)
        # first_name, last_name, username, email, password)
    if not register.success:
        session['logged_in'] = False
        session['user_id'] = None
        return Func_Result(False, None)
    session['logged_in'] = True
    session['user_id'] = register.result
    return Func_Result(True, {'registered': True})

def try_login(username: str, password: str) -> Func_Result:
    check_user = db_check_user(username)
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
    threading.Thread(target=rd_clear_user_sessions, args=(session['user_id'],)).start()
    
def check_login() -> bool:
    return 'logged_in' in session and session['logged_in'] and 'user_id' in session and session['user_id']

def check_admin() -> bool:
    return 'is_admin' in session and session['is_admin']

def get_server_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def check_unique_register_input(type: str, value: str) -> Func_Result:
    unique_check = db_check_unique_register_input(type, value)
    if not unique_check.success:
        return Func_Result(False, None)
    return Func_Result(True, {'unique': unique_check.result})

def get_profile() -> Func_Result:
    user_id = session['user_id']
    profile = db_get_profile(user_id)
    if not profile.success:
        print('Error getting profile')
        return Func_Result(False, profile.result)
    return Func_Result(True, Profile(
        username=profile.result[0],
        created_time=profile.result[1].strftime('%m/%d/%Y'),
        points=profile.result[2],
        num_top10=profile.result[3],
        ranks=sorted(profile.result[4], key=lambda x: (x['rank'], x['game_name']))
    ))

