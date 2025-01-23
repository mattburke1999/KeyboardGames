from flask import render_template
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

def json_result(result):
        return (jsonify(result[1]), 200) if result[0] else (jsonify(result[1]), 500)

def home_view():
    home_page_results = get_home_page_data()
    return render_template('index.html', games=home_page_results[1]['games'], game_info=home_page_results[1]['game_info'], logged_in=home_page_results[1]['logged_in'])

def game_view(game):
    game_info_results = get_game_info(game)
    if not game_info_results[0]:
        return render_template('404.html'), 404
    game_info = game_info_results[1]['game_info']
    if game_info['basic_circle_template']:
        return basic_circle_template(game, game_info, logged_in=game_info_results[1]['logged_in'], ip=game_info_results[1]['ip'], user_skin=game_info_results[1]['user_skin'])
    return render_template(f'{game}.html', game_info=game_info, logged_in=game_info_results[1]['logged_in'], ip=game_info_results[1]['ip'], user_skin=game_info_results[1]['user_skin'])

def basic_circle_template(game, game_info, logged_in, ip, user_skin):
    return render_template('basic_circle_template.html', game=game, game_info=game_info, logged_in=logged_in, ip=ip, user_skin=user_skin)

def auth_view(page):
    return render_template('login.html', page=page)

def check_unique_register_input_view(type, value):
    result = check_unique_register_input(type, value)
    return json_result(result)

def register_view(first_name, last_name, username, email, password):
    result = create_user(first_name, last_name, username, email, password)
    return json_result(result)

def login_view(username, password):
    result = try_login(username, password)
    return json_result(result)

def logout_view():
    logout()
    return json_result((True, {}))

def create_session_view():
    result = create_session()
    return json_result(result)

def profile_view():
    result = get_profile()
    return json_result(result)

def score_update_view(game_id, score, start_game_token, end_game_token, point_list):
    result = score_update(game_id, score, start_game_token, end_game_token, point_list)
    return json_result(result)

def skins_view():
    all_skins = get_all_skins()
    return render_template('skins.html', all_skins=all_skins[1]['skins'], points=all_skins[1]['points'])

def get_skin_view(page, skin):
    return render_template('skin_macros/skin_render.html', page=page, skin=skin)

def set_user_skin_view(skin_id):
    result = set_user_skin(skin_id)
    return json_result(result)