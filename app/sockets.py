from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import disconnect
from flask_socketio import join_room
from services import get_game_duration
import threading
import uuid
from time import sleep

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print("Client connected")
        
@socketio.on('disconnect')
def user_disconnects():
    disconnect()
    print("User disconnected")
    
GAME_ROOMS = {}

@socketio.on('enter_game_room')
def enter_game_room(user_id, game_id):
    global GAME_ROOMS
    duration_result = get_game_duration(game_id)
    if not duration_result[0]:
        return {'success': False, 'message': 'Error getting game duration'}
    duration = float(duration_result[1])
    GAME_ROOMS[user_id] = {'game_id': game_id, 'duration': duration}
    join_room(user_id)
    return {'success': True}

def timer_for_game(user_id, game_id, duration, end_game_token):
    sleep(duration)
    emit_end_game(user_id, game_id, end_game_token)
        
def emit_end_game(user_id, game_id, end_game_token):
    emit('end_game', {'game_id': game_id, 'end_game_token': end_game_token}, room=user_id)    
    

@socketio.on('start_game')
def start_game(user_id, game_id):
    global GAME_ROOMS
    if user_id not in GAME_ROOMS:
        return {'success': False, 'message': 'User not in game room'}
    if GAME_ROOMS[user_id]['game_id'] != game_id:
        return {'success': False, 'message': 'User not in game room'}
    start_game_token = str(uuid.uuid4())
    end_game_token = str(uuid.uuid4())
    GAME_ROOMS[user_id]['start_game_token'] = start_game_token
    GAME_ROOMS[user_id]['end_game_token'] = end_game_token
    # start a timer thread
    threading.Thread(target=timer_for_game, args=(user_id, game_id, GAME_ROOMS[user_id]['duration'], GAME_ROOMS[user_id]['end_game_token'])).start()
    return {'success': True, 'start_game_token': start_game_token}