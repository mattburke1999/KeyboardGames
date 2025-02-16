from flask import session
from app.data_access.models import Func_Result
from .data_access.db import ProfileDB

DB = ProfileDB()

def get_profile() -> Func_Result:
    user_id = session['user_id']
    try:
        profile = DB.get_profile(user_id)
        return Func_Result(True, profile)
    except Exception as e:
        print('Error getting profile')
        return Func_Result(False, {'error': 'Error getting profile', 'message': str(e)})