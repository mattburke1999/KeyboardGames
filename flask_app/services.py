from db import get_games as db_get_games
from db import check_unique_register_input as db_check_unique_register_input
from db import create_user as db_create_user
from db import check_user as db_check_user
from db import get_profile as db_get_profile
from db import create_user_session as db_create_user_session
from db import clear_user_sessions as db_clear_user_sessions
from db import get_user_session as db_get_user_session
from db import update_score as db_update_score
from db import get_all_skins as db_get_all_skins
from db import set_user_skin as db_set_user_skin
from db import get_user_skin as db_get_user_skin
from db import get_default_skin as db_get_default_skin
from db import check_skin_purchaseable as db_check_skin_purchaseable
from db import purchase_skin as db_purchase_skin
from flask import session
import bcrypt
import jwt
import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import threading
import socket
import requests

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

def get_current_user():
    if 'logged_in' in session and session['logged_in']:
        return (True, {'logged_in': True})
    return (True, {'logged_in': False})

def get_user_jwt():
    if 'logged_in' in session and session['logged_in'] and 'user_jwt' in session and session['user_jwt']:
        return (True, {'logged_in': True, 'user_jwt': session['user_jwt']})
    return (True, {'logged_in': False, 'user_jwt': None})

def create_session(client_ip):
    client_ip = client_ip.replace('127.0.0.1', get_server_ip())
    user_id = session['user_id']
    session_result = db_create_user_session(user_id, client_ip)
    if not session_result[0]:
        return (False, session_result[1])
    session_jwt = create_session_jwt(session_result[1], client_ip)
    return (True, {'session_jwt': session_jwt, 'logged_in': True})

def get_user_session():
    user_id = session['user_id']
    session_result = db_get_user_session(user_id)
    if not session_result[0]:
        return (False, session_result[1])
    return (True, {'session_jwt': session_result[1]})

def create_session_jwt(session_id, client_ip):
    secret_key = os.getenv('SHARED_SECRET_KEY')
    # set expiration to 10 seconds
    date_exp = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
    jwt_token = jwt.encode({'session_id': str(session_id), 'client_ip': client_ip, 'exp': int(date_exp.timestamp())}, secret_key, algorithm='HS256')
    session['session_jwt'] = str(jwt_token)
    session['client_ip'] = client_ip
    return jwt_token

def create_user(first_name, last_name, username, email, password):
    register_result = db_create_user(first_name, last_name, username, email, password)
    if not register_result[0]:
        session['logged_in'] = False
        session['user_id'] = None
        return (False, None)
    session['logged_in'] = True
    session['user_id'] = register_result[1]
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
    # create a thread to clear user sessions in the background so this returns immediately
    threading.Thread(target=db_clear_user_sessions, args=(session['user_id'],)).start()
    
def check_login():
    return 'logged_in' in session and session['logged_in'] and 'user_id' in session and session['user_id']

def get_server_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_user_skin():
    user_id = session['user_id']
    skin_result = db_get_user_skin(user_id)
    if not skin_result[0]:
        return (False, skin_result[1])
    return (True, {
        'type': skin_result[1][0],
        'name': skin_result[1][1],
        'data': skin_result[1][2]
    })

def get_game_info(game):
    global GAME_INFO
    if not GAME_INFO:
        games_result = get_games()
        if not games_result[0]:
            return (False, {'error': 'No games found', 'type': 404})
    if game not in GAME_INFO:
        return (False, {'error': 'Game not found', 'type': 404})
    user_skin_result = get_user_skin()
    if not user_skin_result[0]:
        user_skin_result = db_get_default_skin()
        if not user_skin_result[0]:
            return (False, {'error': user_skin_result[1], 'message': 'Unable to load game', 'type': 500})
    return (True, {'game_info': GAME_INFO[game], 'logged_in': check_login(), 'ip': get_server_ip(), 'user_skin': user_skin_result[1]})

def check_unique_register_input(type, value):
    result = db_check_unique_register_input(type, value)
    if not result[0]:
        return (False, None)
    return (True, {'unique': result[1]})

def get_profile():
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

def validate_points(server_point_list, client_point_list, score):
    # print('Server points:')
    # print(server_point_list)
    # print('Client points:')
    # print(client_point_list)
    # print(f'Score: {score}')
    latency_tolerance = timedelta(seconds=1.5)
    if len(server_point_list) < len(client_point_list) or score > len(server_point_list) or score > len(client_point_list):
        return (False, {'error': 'Too many points submitted'})
    for point in client_point_list:
        # point: {'point_token': point_token, 'point_time': point_time}
        server_matching_point = next((p for p in server_point_list if p['point_token'] == point['point_token']), None)
        if not server_matching_point:
            return (False, {'error': 'Invalid point submitted'})
        try:
            server_time = datetime.fromisoformat(server_matching_point['point_time'])
            client_time = datetime.fromisoformat(point['point_time'])
        except ValueError:
            return (False, {'error': 'Invalid time format submitted'})
        actual_latency = abs(server_time - client_time)
        print(f'Actual latency: {actual_latency}')
        # Validate time difference within latency tolerance
        if actual_latency > latency_tolerance:
            print(f'Server time: {server_time}')
            print(f'Client time: {client_time}')
            return (False, {'error': 'Invalid point time submitted'})
    return (True, {'points': len(server_point_list)})      

def validate_game(client_data, server_data, score):
    if not client_data['start_game_token'] == server_data['start_game_token'] or not client_data['end_game_token'] == server_data['end_game_token']:
        return (False, {'error': 'Invalid start and end tokens'})
    point_validation_result = validate_points(server_data['point_list'], client_data['point_list'], score)
    if not point_validation_result[0]:
        return (False, point_validation_result[1])
    return (True, point_validation_result[1])

def fetch_game_room_data(session_jwt):
    response = requests.post(f'http://127.0.0.1:3030/get_session_data', headers={'Authorization': f'{session_jwt}'})
    if response.status_code != 200:
        return (False, {'error': 'Error fetching game room data'})
    data = response.json()
    if 'error' in data:
        return (False, {'error': data['error']})
    return (True, data)

def score_update(game_id, client_ip, score, start_game_token, end_game_token, point_list):
    user_id = session['user_id']
    session_jwt = session.get('session_jwt', None)
    if not session_jwt:
        return (False, {'error': 'No session token'})
    server_data_result = fetch_game_room_data(session_jwt)
    # delete session as soon as the data is fetched
    threading.Thread(target=db_clear_user_sessions, args=(user_id,)).start()
    if not server_data_result[0]:
        return (False, server_data_result[1])
    client_data = {
        'start_game_token': start_game_token,
        'end_game_token': end_game_token,
        'point_list': point_list
    }
    server_data = {
        'start_game_token': server_data_result[1]['start_game_token']['String'],
        'end_game_token': server_data_result[1]['end_game_token']['String'],
        'point_list': server_data_result[1]['point_list']['List']
    }
    validation_result = validate_game(client_data, server_data, score)
    if not validation_result[0]:
        return (False, validation_result[1])
    score = validation_result[1]['points']
    print(f'Score validated, uploading score: {score} for user {user_id} in game {game_id}')
    update_result = db_update_score(user_id, game_id, score)
    if not update_result[0]:
        return (False, update_result[1])
    high_scores, points_added, score_rank = update_result[1]
    # format date as mm/dd/yyyy
    top10 = [{
        **hs,
        'date': datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'),
        'current_score': hs['current_score']
        } for hs in high_scores if hs['score_type'] == 'top10']
    top3 = [{
        'score': hs['score'],
        'date': datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'),
        'current_score': hs['current_score']
        } for hs in high_scores if hs['score_type'] == 'top3']
    return (True, {'top10': top10, 'top3': top3, 'points_added': points_added, 'score_rank': score_rank})

def get_all_skins():
    user_id = session['user_id']
    all_skins_result = db_get_all_skins(user_id)
    if not all_skins_result[0]:
        return (False, all_skins_result[1])
    skin_list = all_skins_result[1][1]
    #sort
    skin_list.sort(key=lambda x: (x['points'], x['id']))
    return (True, {
            'points': all_skins_result[1][0],
            # sort by points ascending, then id ascending
            'skins': skin_list
        })
    
def set_user_skin(skin_id):
    user_id = session['user_id']
    set_skin_result = db_set_user_skin(user_id, skin_id)
    if not set_skin_result[0]:
        return (False, set_skin_result[1])
    return (True, {'success': True})

def purchase_skin(skin_id):
    user_id = session['user_id']
    skin_purchaseable_result = db_check_skin_purchaseable(user_id, skin_id)
    if not skin_purchaseable_result[0]:
        return (False, skin_purchaseable_result[1])
    if not skin_purchaseable_result[1]:
        return (False, {'error': 'Not enought points.'})
    purchase_skin_result = db_purchase_skin(user_id, skin_id)
    if not purchase_skin_result[0]:
        return (False, purchase_skin_result[1])
    return (True, {'success': True})