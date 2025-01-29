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
from services import get_skin_inputs
from services import create_new_skin
from functools import wraps
from typing import Callable
from models import New_User
from models import Skin
from models import New_Skin
from models import Game_Data
from models import Game_Page

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
            return json_result((False, {'is_admin': False, 'message': 'You must be an admin to access this page.'}))
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
            return json_result((False, {'logged_in': False, 'message': 'You must be logged in to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def json_result(result: tuple[bool, any]): # type: ignore
    if result[0]:
        return (jsonify(result[1]), 200) 
    else:
        if result[1] and 'logged_in' in result[1] and not result[1]['logged_in']:
            return (jsonify(result[1]), 401)
        return (jsonify(result[1]), 500)

# page
def home_view():
    home_page_result = get_home_page_data()
    if not home_page_result[0] or not home_page_result[1]:
        return render_template('505.html'), 505
    home_page = home_page_result[1]
    return render_template('index.html', home_page=home_page)

# page
def game_view(game: str):
    game_info_result = get_game_info(game)
    if not game_info_result[0] and type(game_info_result[1]) == dict:
        return render_template(f"{game_info_result[1]['type']}.html", message=game_info_result[1]['message']), game_info_result[1]['type']
    game_page = game_info_result[1]
    if game_page.game_info.basic_circle_template: # type: ignore
        return basic_circle_template(game, game_page) # type: ignore
    return render_template(f'{game}.html', game_page=game_page)

# page
def basic_circle_template(game: str, game_page: Game_Page):
    return render_template('basic_circle_template.html', game=game, game_page=game_page)

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
def create_session_view(client_ip):
    session_result = create_session(client_ip)
    return json_result(session_result)

# endpoint
def profile_view():
    result = get_profile()
    return json_result(result)

# endpoint
def score_update_view(game_id: int, client_ip: str|None, client_game_data: Game_Data, score: int):
    result = score_update(game_id, client_ip, client_game_data, score)
    return json_result(result)

# page
def skins_view():
    skins_page_result = get_all_skins()
    if not skins_page_result[0]:
        return render_template('505.html'), 505
    skins_page = skins_page_result[1]
    return render_template('skins.html', skins_page=skins_page)

# endpoint
def get_skin_view(page: str, skin: Skin):
    return json_result((True, {'html': render_template('skin_macros/skin_render.html', page=page, skin=skin)}))

# endpoint
def set_user_skin_view(skin_id: int):
    result = set_user_skin(skin_id)
    return json_result(result)

# endpoint
def purchase_skin_view(skin_id: int):
    result = purchase_skin(skin_id)
    return json_result(result)

# page 
def create_skin_view():
    skin_input_result = get_skin_inputs()
    if not skin_input_result[0]:
        return render_template('505.html'), 505
    return render_template('create_skin.html', new_skin_page = {'inputs': skin_input_result[1]})

# page
def create_new_skin_view(new_skin: New_Skin):
    result = create_new_skin(new_skin)
    return json_result(result)