from flask import render_template
from flask import redirect
from flask import jsonify
from services import get_home_page_data
from services import get_game_info
from services import check_unique_register_input
from services import create_user
from services import try_login
from services import logout
from services import create_session
from services import get_profile
from services import score_update
from services import get_all_skins
from services import set_user_skin
from services import purchase_skin
from services import check_login
from services import check_admin
from functools import wraps

def admin_page(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def admin_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin():
            return json_result((False, {'is_admin': False, 'message': 'You must be an admin to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def login_required_page(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def login_required_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_login():
            return json_result((False, {'logged_in': False, 'message': 'You must be logged in to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def json_result(result):
    if result[0]:
        return (jsonify(result[1]), 200) 
    else:
        if result[1] and 'logged_in' in result[1] and not result[1]['logged_in']:
            return (jsonify(result[1]), 401)
        return (jsonify(result[1]), 500)

# page
def home_view():
    home_page_results = get_home_page_data()
    return render_template('index.html', games=home_page_results[1]['games'], game_info=home_page_results[1]['game_info'], logged_in=home_page_results[1]['logged_in'])

# page
def game_view(game):
    game_info_results = get_game_info(game)
    if not game_info_results[0]:
        return render_template(f"{game_info_results[1]['type']}.html", message=game_info_results[1]['message']), game_info_results[1]['type']
    game_info = game_info_results[1]['game_info']
    if game_info['basic_circle_template']:
        return basic_circle_template(game, game_info, logged_in=game_info_results[1]['logged_in'], ip=game_info_results[1]['ip'], user_skin=game_info_results[1]['user_skin'])
    return render_template(f'{game}.html', game_info=game_info, logged_in=game_info_results[1]['logged_in'], ip=game_info_results[1]['ip'], user_skin=game_info_results[1]['user_skin'])

# page
def basic_circle_template(game, game_info, logged_in, ip, user_skin):
    return render_template('basic_circle_template.html', game=game, game_info=game_info, logged_in=logged_in, ip=ip, user_skin=user_skin)

# page
def auth_view(page):
    return render_template('login.html', page=page)

# endpoint
def check_unique_register_input_view(type, value):
    result = check_unique_register_input(type, value)
    return json_result(result)

# endpoint
def register_view(first_name, last_name, username, email, password):
    result = create_user(first_name, last_name, username, email, password)
    return json_result(result)

# endpoint
def login_view(username, password):
    result = try_login(username, password)
    return json_result(result)

# endpoint
def logout_view():
    logout()
    return redirect('/')

# endpoint
@login_required_endpoint
def create_session_view(client_ip):
    session_result = create_session(client_ip)
    return json_result(session_result)

# endpoint
@login_required_endpoint
def profile_view():
    result = get_profile()
    return json_result(result)

# endpoint
@login_required_endpoint
def score_update_view(game_id, client_ip, score, start_game_token, end_game_token, point_list):
    result = score_update(game_id, client_ip, score, start_game_token, end_game_token, point_list)
    return json_result(result)

# page
@login_required_page
def skins_view():
    all_skins_results = get_all_skins()
    if not all_skins_results[0]:
        return render_template('505.html'), 505
    return render_template('skins.html', all_skins=all_skins_results[1]['skins'], points=all_skins_results[1]['points'])

# endpoint
@login_required_endpoint
def get_skin_view(page, skin):
    return json_result((True, {'html': render_template('skin_macros/skin_render.html', page=page, skin=skin)}))

# endpoint
@login_required_endpoint
def set_user_skin_view(skin_id):
    result = set_user_skin(skin_id)
    return json_result(result)

# endpoint
@login_required_endpoint
def purchase_skin_view(skin_id):
    result = purchase_skin(skin_id)
    return json_result(result)
