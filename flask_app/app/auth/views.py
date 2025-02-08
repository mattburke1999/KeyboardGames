from flask import render_template
from flask import abort
from flask import redirect
from app.views import json_result
from app.data_access.models import Func_Result

# page
def auth_view(page: str):
    return render_template('login.html', page=page)
   
# endpoint
def not_logged_in_view(type: str):
    if type == 'api':
        return json_result(Func_Result(False, {'logged_in': False, 'message': 'You must be logged in to access this page.'}))
    return redirect('/')

# endpoint
def not_admin_view(type: str):
    if type == 'api':
        return json_result(Func_Result(False, {'is_admin': False, 'message': 'You must be an admin to access this page.'}))
    return redirect('/')

def not_localhost_view(type: str):
    if type == 'api':
        abort(403)
    return redirect('/')