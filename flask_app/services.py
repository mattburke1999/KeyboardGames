from db import get_games as db_get_games
from db import check_unique_register_input as db_check_unique_register_input
from db import create_user as db_create_user
from db import check_user as db_check_user
from db import get_profile as db_get_profile
from flask import session
import bcrypt

GAME_INFO = {}
GAMES = []

def get_home_page_data():
    games_result = get_games()
    if not games_result[0]:
        return (False, None)
    logged_in = check_login()
    return (True, {'games': games_result[1][1], 'game_info': games_result[1][0], 'logged_in': logged_in})

def get_games():
    global GAME_INFO
    global GAMES
    if len(GAMES) == 0:
        game_results = db_get_games()
        if not game_results[0]:
            return (False, None)
        for game in game_results[1]:
            GAMES.append(game[7])
            GAME_INFO[game[7]] = {
                'id': game[0],
                'title': game[1],
                'title_style': game[2],
                'title_color': game[3],
                'bg_rot': game[4],
                'bg_color1': game[5],
                'bg_color2': game[6],
                'duration': game[8],
                'basic_circle_template': game[9]
            }
    return (True, (GAME_INFO, GAMES))

def get_user_id():
    if 'logged_in' in session and session['logged_in'] and 'user_id' in session and session['user_id']:
        return (True, {'logged_in': True, 'user_id': session['user_id']})
    return (True, {'logged_in': False, 'user_id': None})
    

def create_user(first_name, last_name, username, email, password):
    register_result = db_create_user(first_name, last_name, username, email, password)
    if not register_result[0]:
        session['logged_in'] = False
        session['user_id'] = None
        return (False, None)
    session['logged_in'] = True
    session['user_id'] = int(register_result[1])
    return (True, {'registered': True})

def try_login(username, password):
    result = db_check_user(username)
    if not result[0]:
        return (False, None)
    if result[1]:
        user_id, hashed_password = result[1]
        if bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hashed_password)):
            session['logged_in'] = True
            session['user_id'] = user_id
            return (True, {'logged_in': True})
    return (True, {'logged_in': False})

def logout():
    session['logged_in'] = False
    session['user_id'] = None

def check_login():
    return 'logged_in' in session and session['logged_in']

def get_game_info(game):
    global GAME_INFO
    if not GAME_INFO:
        games_result = get_games()
        if not games_result[0]:
            return (False, {'error': 'No games found'})
    if game not in GAME_INFO:
        return (False, {'error': 'Game not found'})
    return (True, {'game_info': GAME_INFO[game], 'logged_in': check_login()})

def check_unique_register_input(type, value):
    result = db_check_unique_register_input(type, value)
    if not result[0]:
        return (False, None)
    return (True, {'unique': result[1]})

def get_profile():
    if not check_login():
        print('Not logged in')
        return (False, {'error': 'Not logged in'})
    user_id = session['user_id']
    profile_result = db_get_profile(user_id)
    if not profile_result[0]:
        print('Error getting profile')
        return (False, profile_result[1])
    return (True, {
        'username': profile_result[1][0],
        'created_time': profile_result[1][1].strftime('%m/%d/%Y'),
        'points': profile_result[1][2],
        'num_top10': profile_result[1][3],
        'ranks': sorted(profile_result[1][4], key=lambda x: (x['rank'], x['game_name']))
    })
