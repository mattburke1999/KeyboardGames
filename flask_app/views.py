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
from services import create_skin_page
from services import create_new_skin_type
from services import create_new_skin_input
from functools import wraps
from typing import Callable
from models import New_User
from models import Skin
from models import New_Skin_Type
from models import New_Skin_Input
from models import Game_Data
from models import Game_Page
from models import Func_Result

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
            return json_result(Func_Result(False, {'is_admin': False, 'message': 'You must be an admin to access this page.'}))
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
            return json_result(Func_Result(False, {'logged_in': False, 'message': 'You must be logged in to access this page.'}))
        return f(*args, **kwargs)
    return decorated_function

def json_result(result: Func_Result):
    if result.success:
        return (jsonify(result.result), 200) 
    else:
        if result.result and 'logged_in' in result.result and not result.result['logged_in']:
            return (jsonify(result.result), 401)
        return (jsonify(result.result), 500)

# page
def home_view():
    home_page = get_home_page_data()
    if not home_page.success or not home_page.result:
        return render_template('505.html'), 505
    return render_template('index.html', home_page=home_page.result)

# page
def game_view(game: str):
    game_info = get_game_info(game)
    if not game_info.success and type(game_info.result) == dict:
        return render_template(f"{game_info.result['type']}.html", message=game_info.result['message']), game_info.result['type']
    game_page = game_info.result
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
    skins_page = get_all_skins()
    if not skins_page.success:
        return render_template('505.html'), 505
    return render_template('skins.html', skins_page=skins_page.result)

# endpoint
def get_skin_view(page: str, skin: Skin):
    return json_result(Func_Result(True, {'html': render_template('skin_macros/skin_render.html', page=page, skin=skin)}))

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
    create_skin = create_skin_page()
    if not create_skin.success:
        return render_template('505.html'), 505
    return render_template('create_skin.html', new_skin_page = create_skin.result)

# endpoint
def create_new_skin_view(new_skin: New_Skin_Type):
    result = create_new_skin_type(new_skin)
    return json_result(result)

# endpoint
def create_skin_inputs_view(new_skin_input: New_Skin_Input):
    result = create_new_skin_input(new_skin_input)
    return json_result(result)