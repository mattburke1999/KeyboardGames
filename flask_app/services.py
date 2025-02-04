from models import Func_Result
from models import Home_Page
from models import Game_Page
from db import get_games as db_get_games
from models import Game_Info
from db import check_unique_register_input as db_check_unique_register_input
from db import create_user as db_create_user
from models import New_User
from db import check_user as db_check_user
from db import get_profile as db_get_profile
from models import Profile
from db import update_score as db_update_score
from models import Game_Data
from models import Score_View
from models import Top10_Score
from models import Top3_Score
from redis_store import create_user_session as rd_create_user_session
from redis_store import clear_user_sessions as rd_clear_user_sessions
from redis_store import get_game_data as rd_get_game_data
from flask import session
import bcrypt
import jwt
import json
import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import threading
import socket

from flask_app.skins.services import get_user_skin
from flask_app.skins.services import get_default_skin

GAME_INFO = {}
GAMES = []

def get_home_page_data() -> Func_Result:
    games = get_games()
    if not games.success or not games.result:
        return Func_Result(False, None)
    logged_in = check_login()
    print(f'service logged_in: {logged_in}')
    return Func_Result(True, Home_Page(games.result[1], games.result[0], logged_in))

def get_games() -> Func_Result:
    global GAME_INFO
    global GAMES
    if len(GAMES) == 0:
        games = db_get_games()
        if not games.success or not games.result:
            return Func_Result(False, None)
        for game in games.result:
            GAMES.append(game[7])
            GAME_INFO[game[7]] = Game_Info(int(game[0]), game[1], game[2], game[3], int(game[4]), game[5], game[6], int(game[8]), game[9])
    return Func_Result(True, (GAME_INFO, GAMES))

def get_current_user() -> Func_Result:
    if 'logged_in' in session and session['logged_in']:
        return Func_Result(True, {'logged_in': True})
    return Func_Result(True, {'logged_in': False})

def get_user_jwt() -> Func_Result:
    if 'logged_in' in session and session['logged_in'] and 'user_jwt' in session and session['user_jwt']:
        return Func_Result(True, {'logged_in': True, 'user_jwt': session['user_jwt']})
    return Func_Result(True, {'logged_in': False, 'user_jwt': None})

def create_session(client_ip: str) -> Func_Result:
    client_ip = client_ip.replace('127.0.0.1', get_server_ip())
    user_id = session['user_id']
    session_created = rd_create_user_session(user_id, client_ip)
    if not session_created.success:
        return Func_Result(False, session_created.result)
    session_jwt = create_session_jwt(session_created.result, client_ip)
    return Func_Result(True, {'session_jwt': session_jwt, 'logged_in': True})

def create_session_jwt(session_id: str, client_ip: str) -> str:
    secret_key = os.getenv('SHARED_SECRET_KEY')
    # set expiration to 10 seconds
    date_exp = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
    jwt_token = jwt.encode({'session_id': str(session_id), 'client_ip': client_ip, 'exp': int(date_exp.timestamp())}, secret_key, algorithm='HS256')
    session['session_jwt'] = str(jwt_token)
    session['client_ip'] = client_ip
    return jwt_token

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

def get_game_info(game: str) -> Func_Result:
    global GAME_INFO
    if not GAME_INFO:
        games = get_games()
        if not games.success:
            return Func_Result(False, {'error': 'No games found', 'type': 404})
    if game not in GAME_INFO:
        return Func_Result(False, {'error': 'Game not found', 'type': 404})
    user_skin = Func_Result(False, None)
    if check_login():
        user_skin = get_user_skin()
    if not user_skin.success or not user_skin.result:
        default_skin = get_default_skin()
        if not default_skin.success:
            return Func_Result(False, {'error': default_skin.result, 'message': 'Unable to load game', 'type': 500})
        user_skin.result = default_skin.result
    return Func_Result(True, Game_Page(GAME_INFO[game], check_login(), get_server_ip(), user_skin.result))

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

def validate_points(server_point_list: list, client_point_list: list, score: int) -> Func_Result:
    # print('Server points:')
    # print(server_point_list)
    # print('Client points:')
    # print(client_point_list)
    # print(f'Score: {score}')
    latency_tolerance = timedelta(seconds=1.5)
    if len(server_point_list) < len(client_point_list) or score > len(server_point_list) or score > len(client_point_list):
        return Func_Result(False, {'error': 'Too many points submitted'})
    for point in client_point_list:
        # point: {'point_token': point_token, 'point_time': point_time}
        server_matching_point = next((p for p in server_point_list if p['point_token'] == point['point_token']), None)
        if not server_matching_point:
            return Func_Result(False, {'error': 'Invalid point submitted'})
        try:
            server_time = datetime.fromisoformat(server_matching_point['point_time'])
            client_time = datetime.fromisoformat(point['point_time'])
        except ValueError:
            return Func_Result(False, {'error': 'Invalid time format submitted'})
        actual_latency = abs(server_time - client_time)
        print(f'Actual latency: {actual_latency}')
        # Validate time difference within latency tolerance
        if actual_latency > latency_tolerance:
            print(f'Server time: {server_time}')
            print(f'Client time: {client_time}')
            return Func_Result(False, {'error': 'Invalid point time submitted'})
    return Func_Result(True, {'points': len(server_point_list)})      

def validate_game(client_data: Game_Data, server_data: Game_Data, score: int) -> Func_Result:
    if not client_data.start_game_token == server_data.start_game_token or not client_data.end_game_token == server_data.end_game_token:
        return Func_Result(False, {'error': 'Invalid start and end tokens'})
    return validate_points(server_data.point_list, client_data.point_list, score)

def score_update(game_id: int, client_ip: str|None, client_data: Game_Data, score: int) -> Func_Result:
    if not client_ip:
        return Func_Result(False, {'error': 'No client IP'})
    user_id = session['user_id']
    session_jwt = session.get('session_jwt', None)
    if not session_jwt:
        return Func_Result(False, {'error': 'No session token'})
    server_data = rd_get_game_data(session_jwt)
    # delete session as soon as the data is fetched
    threading.Thread(target=rd_clear_user_sessions, args=(user_id, client_ip)).start()
    if not server_data.success:
        return Func_Result(False, server_data.result)
    server_data = Game_Data(**json.loads(server_data.result))
    validation = validate_game(client_data, server_data, score)
    if not validation.success:
        return Func_Result(False, validation.success)
    score = int(validation.result['points'])
    print(f'Score validated, uploading score: {score} for user {user_id} in game {game_id}')
    score_update = db_update_score(user_id, game_id, score)
    if not score_update.success:
        return Func_Result(False, score_update.result)
    high_scores, points_added, score_rank = score_update.result
    # format date as mm/dd/yyyy
    top10 = [Top10_Score(hs['username'], hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
        for hs in high_scores if hs['score_type'] == 'top10']
    top3 = [Top3_Score(hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
        for hs in high_scores if hs['score_type'] == 'top3']
    return Func_Result(True, Score_View(top10, top3, points_added, score_rank))
