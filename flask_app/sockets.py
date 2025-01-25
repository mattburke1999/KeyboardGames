from flask_socketio import SocketIO
from flask import session
from flask_socketio import disconnect
from services import check_login

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print("Client connected")
        
@socketio.on('disconnect')
def user_disconnects():
    disconnect()
    print("User disconnected")
    
@socketio.on('join_session')
def join_session():
    if not check_login():
        return disconnect()
    return (True, {'joined_room': True})

@socketio.on('get_session')
def get_session():
    if not check_login():
        return disconnect()
    session_jwt = session.get('session_jwt', None)
    if not session_jwt:
        return disconnect()
    return (True, {'session_jwt': session_jwt})