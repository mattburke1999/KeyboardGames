from flask import session
from app.data_access.models import Func_Result
from .data_access.models import Game_Page
from .data_access.models import Game_Data
from .data_access.db import GameDB
from app.data_access import RD
from app.skins.services import get_user_skin
from app.skins.services import get_default_skin
from app.auth.services import check_login

import os
import jwt
import threading
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import socket
import traceback

GAME_INFO = {}
DB = GameDB()

def get_games_process() -> Func_Result:
    global GAME_INFO
    try:
        if not GAME_INFO:
            GAME_INFO = DB.get_games()
        return Func_Result(True, GAME_INFO)
    except Exception as e:
        traceback.print_exc()
        return Func_Result(False, {'error': str(e)})

def get_game_page(game: str) -> Func_Result:
    global GAME_INFO
    if not GAME_INFO:
        games = get_games_process()
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

def create_session_process(client_ip: str | None) -> Func_Result:
    if not client_ip:
        return Func_Result(False, {'error': 'No client IP'})
    client_ip = client_ip.replace('127.0.0.1', get_server_ip())
    user_id = session['user_id']
    session_id = None
    try:
        session_id = RD.create_user_session(user_id, client_ip)
        session_jwt = create_session_jwt(session_id, client_ip)
        return Func_Result(True, {'session_jwt': session_jwt, 'logged_in': True})
    except Exception as e:
        if session_id:
            threading.Thread(target=RD.clear_user_sessions, args=(user_id, client_ip)).start()
        session['session_jwt'] = None
        session['client_ip'] = None
        return Func_Result(False, {'error': str(e)})

def create_session_jwt(session_id: str, client_ip: str) -> str:
    secret_key = os.getenv('SHARED_SECRET_KEY')
    # set expiration to 10 seconds
    date_exp = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
    jwt_token = jwt.encode({'session_id': str(session_id), 'client_ip': client_ip, 'exp': int(date_exp.timestamp())}, secret_key, algorithm='HS256')
    session['session_jwt'] = str(jwt_token)
    session['client_ip'] = client_ip
    return jwt_token

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

def score_update_process(client_ip: str|None, data: dict, game_id: int) -> Func_Result:
    if not client_ip:
        return Func_Result(False, {'error': 'No client IP'})
    client_data = Game_Data(data['start_game_token'], data['end_game_token'], data['pointList'])
    score = data['score']
    user_id = session['user_id']
    session_jwt = session.get('session_jwt', None)
    if not session_jwt:
        return Func_Result(False, {'error': 'No session token'})
    server_data = None
    try:
        server_data = RD.get_game_data(session_jwt)
    except Exception as e:
        return Func_Result(False, {'error': 'Error fetching game data', 'message': str(e)})
    finally:
        threading.Thread(target=RD.clear_user_sessions, args=(user_id, client_ip)).start()
    if not server_data:
        return Func_Result(False, {'error': 'No server game data'})
    validation = validate_game(client_data, server_data, score)
    if not validation.success:
        return Func_Result(False, validation.success)
    score = int(validation.result['points'])
    print(f'Score validated, uploading score: {score} for user {user_id} in game {game_id}')
    with DB.connect_db() as conn:
        try:
            score_update = DB.update_score(conn, user_id, game_id, score)
            conn.commit()
        except Exception as e:
            conn.rollback()
            return Func_Result(False, {'error': 'Error updating score', 'message': str(e)})
    return Func_Result(True, score_update)

def get_server_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)
