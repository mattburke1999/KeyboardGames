from flask import session
from app.data_access.models import Func_Result
from app.data_access.models import Home_Page
from app.data_access.db import BaseDB
from app.games.services import get_games_process
from app.auth.services import check_login

DB = BaseDB()

def get_home_page_data() -> Func_Result:
    games = get_games_process()
    if not games.success or not games.result:
        return Func_Result(False, None)
    logged_in = check_login()
    return Func_Result(True, Home_Page(games.result, logged_in))

def get_profile() -> Func_Result:
    user_id = session['user_id']
    try:
        profile = DB.get_profile(user_id)
        return Func_Result(True, profile)
    except Exception as e:
        print('Error getting profile')
        return Func_Result(False, {'error': 'Error getting profile', 'message': str(e)})


