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
from views import skins_view
from views import get_skin_view
from views import set_user_skin_view
from views import purchase_skin_view
from views import create_skin_view
from views import create_new_skin_view
from views import login_required_endpoint
from views import login_required_page
from views import admin_page
from models import NewUser
from models import Skin
from models import Game_Data

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/<game_name>', methods=['GET']) # type: ignore
def game(game_name: str):
    return game_view(game_name)

@app.route('/login', methods=['GET'])
def login():
    return auth_view('login')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()['formData']
    return login_view(data['username'], data['password'])

@app.route('/logout', methods=['GET'])
def logout():
    return logout_view()

@app.route('/register', methods=['GET'])
def register():
    return auth_view('register')

@app.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()['formData']
    new_user = NewUser(data['first_name'], data['last_name'], data['username'], data['email'], data['password'])
    return register_view(new_user)

@app.route('/unique_username', methods=['POST'])
def unique_username():
    data = request.get_json()
    return check_unique_register_input_view('username', data['username'])

@app.route('/unique_email', methods=['POST'])
def unique_email():
    data = request.get_json()
    return check_unique_register_input_view('email', data['email'])

@login_required_endpoint
@app.route('/create_session', methods=['GET'])
def create_session():
    client_ip = request.remote_addr
    return create_session_view(client_ip)

@login_required_endpoint
@app.route('/profile', methods=['GET'])
def profile():
    return profile_view()

@login_required_endpoint
@app.route('/game/<game_id>/score_update', methods=['POST'])
def score_update(game_id):
    data = request.get_json()
    client_ip = request.remote_addr
    client_game_data = Game_Data(data['start_game_token'], data['end_game_token'], data['pointList'])
    return score_update_view(game_id, client_ip, client_game_data, data['score'])

@login_required_page
@app.route('/skins', methods=['GET'])
def skins():
    return skins_view()

@login_required_endpoint
@app.route('/skins/get_skin', methods=['POST'])
def get_skin():
    data = request.get_json()
    skin = Skin(**data['skin'])
    return get_skin_view(data['page'], skin)

@login_required_endpoint
@app.route('/skins/select', methods=['POST'])
def select_skin():
    data = request.get_json()
    return set_user_skin_view(data['skin_id'])

@login_required_endpoint
@app.route('/skins/purchase', methods=['POST'])
def purchase_skin():
    data = request.get_json()
    return purchase_skin_view(data['skin_id'])

@admin_page
@app.route('/create_skin', methods=['GET'])
def create_skin():
    return create_skin_view()

@admin_page
@app.route('/create_skin', methods=['POST'])
def create_new_skin():
    data = request.get_json()
    return create_new_skin_view()