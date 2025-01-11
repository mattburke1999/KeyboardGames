from flask import Flask
from flask import request
from views import home_view
from views import game_view
from views import auth_view
from views import check_unique_register_input_view
from views import register_view
from views import login_view
from views import logout_view
from views import create_session_view
from views import profile_view
from views import score_update_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/<game_name>', methods=['GET'])
def game(game_name):
    return game_view(game_name)

@app.route('/login', methods=['GET'])
def login():
    return auth_view('login')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()['formData']
    return login_view(data['username'], data['password'])

@app.route('/logout', methods=['POST'])
def logout():
    return logout_view()

@app.route('/register', methods=['GET'])
def register():
    return auth_view('register')

@app.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()['formData']
    return register_view(data['first_name'], data['last_name'], data['username'], data['email'], data['password'])

@app.route('/unique_username', methods=['POST'])
def unique_username():
    data = request.get_json()
    return check_unique_register_input_view('username', data['username'])

@app.route('/unique_email', methods=['POST'])
def unique_email():
    data = request.get_json()
    return check_unique_register_input_view('email', data['email'])

@app.route('/create_session', methods=['GET'])
def create_session():
    return create_session_view()

@app.route('/profile', methods=['GET'])
def profile():
    return profile_view()

@app.route('/game/<game_id>/score_update', methods=['POST'])
def score_update(game_id):
    data = request.get_json()
    return score_update_view(game_id, data['score'], data['start_game_token'], data['end_game_token'], data['pointList'])