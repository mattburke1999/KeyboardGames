from models import Home_Page
from models import Game_Page
from db import connect_db
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
from db import get_all_skins as db_get_all_skins
from models import Skin
from models import Skins_Page
from db import set_user_skin as db_set_user_skin
from db import get_user_skin as db_get_user_skin
from db import get_default_skin as db_get_default_skin
from db import check_skin_purchaseable as db_check_skin_purchaseable
from db import purchase_skin as db_purchase_skin
from db import get_skin_inputs as db_get_skin_inputs
from db import get_skin_input_id_by_name as db_get_skin_input_id_by_name
from db import new_skin_input as db_new_skin_input
from db import create_skin as db_create_skin
from db import get_skin_type_with_inputs as db_get_skin_type_with_inputs
from models import Skin_Input
from models import Skin_Type_With_Inputs
from models import Create_Skin_Page
from db import check_skin_type_exists as db_check_skin_type_exists
from models import New_Skin
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

GAME_INFO = {}
GAMES = []

def get_home_page_data() -> tuple[bool, Home_Page|None]:
    games_result = get_games()
    if not games_result[0] or not games_result[1]:
        return (False, None)
    logged_in = check_login()
    print(f'service logged_in: {logged_in}')
    return (True, Home_Page(games_result[1][1], games_result[1][0], logged_in))

def get_games() -> tuple[bool, tuple[dict[str, Game_Info], list[str]]|None]:
    global GAME_INFO
    global GAMES
    if len(GAMES) == 0:
        games = db_get_games()
        if not games.success or not games.result:
            return (False, None)
        for game in games.result:
            GAMES.append(game[7])
            GAME_INFO[game[7]] = Game_Info(int(game[0]), game[1], game[2], game[3], int(game[4]), game[5], game[6], int(game[8]), game[9])
    return (True, (GAME_INFO, GAMES))

def get_current_user() -> tuple[bool, dict[str, bool]]:
    if 'logged_in' in session and session['logged_in']:
        return (True, {'logged_in': True})
    return (True, {'logged_in': False})

def get_user_jwt() -> tuple[bool, dict[str, bool|str|None]]:
    if 'logged_in' in session and session['logged_in'] and 'user_jwt' in session and session['user_jwt']:
        return (True, {'logged_in': True, 'user_jwt': session['user_jwt']})
    return (True, {'logged_in': False, 'user_jwt': None})

def create_session(client_ip: str) -> tuple[bool, dict[str, str|bool]]:
    client_ip = client_ip.replace('127.0.0.1', get_server_ip())
    user_id = session['user_id']
    session_created = rd_create_user_session(user_id, client_ip)
    if not session_created.success:
        return (False, session_created.result)
    session_jwt = create_session_jwt(session_created.result, client_ip)
    return (True, {'session_jwt': session_jwt, 'logged_in': True})

def create_session_jwt(session_id: str, client_ip: str) -> str:
    secret_key = os.getenv('SHARED_SECRET_KEY')
    # set expiration to 10 seconds
    date_exp = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
    jwt_token = jwt.encode({'session_id': str(session_id), 'client_ip': client_ip, 'exp': int(date_exp.timestamp())}, secret_key, algorithm='HS256')
    session['session_jwt'] = str(jwt_token)
    session['client_ip'] = client_ip
    return jwt_token

def create_user(new_user: New_User) -> tuple[bool, dict[str, bool]|None]:
    # first_name, last_name, username, email, password):
    register = db_create_user(new_user)
        # first_name, last_name, username, email, password)
    if not register.success:
        session['logged_in'] = False
        session['user_id'] = None
        return (False, None)
    session['logged_in'] = True
    session['user_id'] = register.result
    return (True, {'registered': True})

def try_login(username: str, password: str) -> tuple[bool, dict[str, bool]|None]:
    check_user = db_check_user(username)
    if not check_user.success:
        return (False, None)
    if check_user.result:
        user_id, hashed_password, is_admin = check_user.result
        if bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hashed_password)):
            session['logged_in'] = True
            session['user_id'] = user_id
            session['is_admin'] = is_admin
            return (True, {'logged_in': True})
    return (True, {'logged_in': False})

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

def get_user_skin() -> tuple[bool, Skin|str]:
    user_id = session['user_id']
    user_skin = db_get_user_skin(user_id)
    if not user_skin.success:
        return (False, user_skin.result)
    return (True, Skin(user_skin.result[0], user_skin.result[1], user_skin.result[1]))

def get_game_info(game: str) -> tuple[bool, Game_Page | dict[str, str|int]]:
    global GAME_INFO
    if not GAME_INFO:
        games_result = get_games()
        if not games_result[0]:
            return (False, {'error': 'No games found', 'type': 404})
    if game not in GAME_INFO:
        return (False, {'error': 'Game not found', 'type': 404})
    user_skin_result = (False, None)
    user_skin = None
    if check_login():
        user_skin_result = get_user_skin()
        user_skin = user_skin_result[1]
    if not user_skin_result[0] or not user_skin:
        user_skin = db_get_default_skin()
        if not user_skin.success:
            return (False, {'error': user_skin.result, 'message': 'Unable to load game', 'type': 500})
        user_skin = user_skin.result
    return (True, Game_Page(GAME_INFO[game], check_login(), get_server_ip(), user_skin)) # type: ignore

def check_unique_register_input(type: str, value: str) -> tuple[bool, dict[str, bool]|None]:
    unique_check = db_check_unique_register_input(type, value)
    if not unique_check.success:
        return (False, None)
    return (True, {'unique': unique_check.result})

def get_profile() -> tuple[bool, Profile|dict[str, str|None]]: 
    user_id = session['user_id']
    profile = db_get_profile(user_id)
    if not profile.success:
        print('Error getting profile')
        return (False, profile.result)
    return (True, Profile(
        username=profile.result[0],
        created_time=profile.result[1].strftime('%m/%d/%Y'),
        points=profile.result[2],
        num_top10=profile.result[3],
        ranks=sorted(profile.result[4], key=lambda x: (x['rank'], x['game_name']))
    ))

def validate_points(server_point_list: list, client_point_list: list, score: int) -> tuple[bool, dict[str, str|int]]:
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

def validate_game(client_data: Game_Data, server_data: Game_Data, score: int) -> tuple[bool, dict[str, str|int]]:
    if not client_data.start_game_token == server_data.start_game_token or not client_data.end_game_token == server_data.end_game_token:
        return (False, {'error': 'Invalid start and end tokens'})
    point_validation_result = validate_points(server_data.point_list, client_data.point_list, score)
    if not point_validation_result[0]:
        return (False, point_validation_result[1])
    return (True, point_validation_result[1])

def score_update(game_id: int, client_ip: str|None, client_data: Game_Data, score: int) -> tuple[bool, Score_View|dict[str, any]]: # type: ignore
    if not client_ip:
        return (False, {'error': 'No client IP'})
    user_id = session['user_id']
    session_jwt = session.get('session_jwt', None)
    if not session_jwt:
        return (False, {'error': 'No session token'})
    server_data = rd_get_game_data(session_jwt)
    # delete session as soon as the data is fetched
    threading.Thread(target=rd_clear_user_sessions, args=(user_id, client_ip)).start()
    if not server_data.success:
        return (False, server_data.result)
    server_data = Game_Data(**json.loads(server_data.result))
    validation_result = validate_game(client_data, server_data, score)
    if not validation_result[0]:
        return (False, validation_result[1])
    score = int(validation_result[1]['points'])
    print(f'Score validated, uploading score: {score} for user {user_id} in game {game_id}')
    score_update = db_update_score(user_id, game_id, score)
    if not score_update.success:
        return (False, score_update.result)
    high_scores, points_added, score_rank = score_update.result
    # format date as mm/dd/yyyy
    top10 = [Top10_Score(hs['username'], hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
        for hs in high_scores if hs['score_type'] == 'top10']
    top3 = [Top3_Score(hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
        for hs in high_scores if hs['score_type'] == 'top3']
    return (True, Score_View(top10, top3, points_added, score_rank))

def get_all_skins() -> tuple[bool, Skins_Page| dict[str, str|None] | None]:
    user_id = session['user_id']
    all_skins = db_get_all_skins(user_id)
    if not all_skins.success:
        return (False, all_skins.result)
    skin_list = [Skin(**skin) for skin in all_skins.result[1]]
    skin_list.sort(key=lambda x: (x.points, x.type, x.id))
    return (True, Skins_Page(all_skins.result[0], skin_list))
    
def set_user_skin(skin_id: int) -> tuple[bool, dict[str, bool]]:
    user_id = session['user_id']
    set_skin = db_set_user_skin(user_id, skin_id)
    if not set_skin.success:
        return (False, set_skin.result)
    return (True, {'success': True})

def purchase_skin(skin_id: int) -> tuple[bool, dict[str, bool|str]]:
    user_id = session['user_id']
    skin_purchaseable = db_check_skin_purchaseable(user_id, skin_id)
    if not skin_purchaseable.success:
        return (False, skin_purchaseable.result)
    if not skin_purchaseable.result:
        return (False, {'error': 'Not enought points.'})
    purchase_skin = db_purchase_skin(user_id, skin_id)
    if not purchase_skin.success:
        return (False, purchase_skin.result)
    return (True, {'success': True})

def get_skin_types_with_inputs() -> tuple[bool, list[Skin_Type_With_Inputs]|str]:
    skin_types = db_get_skin_type_with_inputs()
    if not skin_types.success:
        return (False, skin_types.result)
    return (True, [Skin_Type_With_Inputs(skin[0], skin[1], [skin[2]]) for skin in skin_types.result])

def get_skin_inputs() -> tuple[bool, list[Skin_Input]|str]:
    skin_inputs = db_get_skin_inputs()
    if not skin_inputs.success:
        return (False, skin_inputs.result)
    return (True, [Skin_Input(skin[0], skin[1]) for skin in skin_inputs.result])

def create_skin_page() -> tuple[bool, Create_Skin_Page|str]:
    skin_types = get_skin_types_with_inputs()
    if not skin_types[0]: 
        return (False, skin_types[1]) # type: ignore
    skin_inputs = get_skin_inputs()
    if not skin_inputs[0]:
        return (False, skin_inputs[1]) # type: ignore
    return (True, Create_Skin_Page(skin_inputs[1], skin_types[1])) # type: ignore

def add_new_skin_inputs(conn, new_skin: New_Skin) -> tuple[bool, dict[str, bool]]:
    for new_input in new_skin.new_inputs:
        input_id = db_get_skin_input_id_by_name(new_input)
        if not input_id.success:
            return (False, input_id.result)
        if input_id.result:
            new_skin.inputs.append(input_id.result)
        else:
            new_input_result = db_new_skin_input(conn, new_input)
            if not new_input_result.success:
                conn.rollback()
                return (False, new_input_result.result)
            new_skin.inputs.append(new_input_result.result)
    return (True, {'success': True})

def add_new_skin_html(new_skin: New_Skin) -> tuple[bool, dict[str, bool|str]]:
    # later we will add some validation checking:
    # - if new_skin.inputs is empty, then skin.data is not in the html
    # - if new_skin.inputs is not empty, then find all skin.data.{input} and make sure any in html are in new_skin.inputs
    macro_name = new_skin.type.replace('-', '_')
    skin_html = "{% macro " + macro_name + "(page, skin) %}\n"
    skin_html += "\t" + new_skin.html + "\n"
    skin_html += "{% endmacro %}"
    # add to /templates/skin_macros/{macro_name}.html
    try:
        with open(f'flask_app/templates/skin_macros/{macro_name}.html', 'w') as f:
            f.write(skin_html)
        return add_new_html_to_mapper(new_skin.type, macro_name)
    except:
        return (False, {'error': 'Error writing skin html'})
    
def add_new_html_to_mapper(type, macro_name) -> tuple[bool, dict[str, bool|str]]:
    try:
        with open('flask_app/templates/skin_macros/skin-mapper.html', 'r') as f:
            skin_mapper = f.read()
    except:
        return (False, {'error': 'Error reading skin mapper'})
    macro_index = skin_mapper.find(macro_name)
    if macro_index == -1:
        end_if = skin_mapper.index('{% endif %}')
        if end_if == -1:
            return (False, {'error': 'Error parsing skin mapper'})
        skin_mapper_pre = skin_mapper[:end_if]
        new_macro_mapper = "{% elif skin.type == '" + type + "' %}\n"
        new_macro_mapper += "\t\t{% from 'skin_macros/" + macro_name + ".html' import " + macro_name + " %}\n"
        new_macro_mapper += "\t\t{{ " + macro_name + "(page, skin) }}\n"
        new_skin_mapper = skin_mapper_pre + new_macro_mapper + "    " + skin_mapper[end_if:]
        try:
            with open('flask_app/templates/skin_macros/skin-mapper.html', 'w') as f:
                f.write(new_skin_mapper)
            return (True, {'success': True})
        except:
            return (False, {'error': 'Error writing skin mapper'})
    return (True, {'success': True})
    
def create_new_skin(new_skin: New_Skin):
    skin_type_exists = db_check_skin_type_exists(new_skin.type)
    if not skin_type_exists.success:
        return (False, skin_type_exists.result)
    if skin_type_exists.result:
        return (False, {'error': 'Skin type already exists'})
    with connect_db() as conn:
        if len(new_skin.new_inputs) > 0:
            add_skin_inputs_result = add_new_skin_inputs(conn, new_skin)
            if not add_skin_inputs_result[0]:
                return add_skin_inputs_result
        create_skin_result = db_create_skin(conn, new_skin)
        if not create_skin_result.success:
            conn.rollback()
            return (False, create_skin_result.result)
    add_new_skin_html_result = add_new_skin_html(new_skin)
    if not add_new_skin_html_result[0]:
        return add_new_skin_html_result
    return (True, {'success': True})