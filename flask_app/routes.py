from flask import Flask
from flask import request
from flask import redirect
from flask import abort
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
from views import admin_endpoint
from models import New_User
from models import Skin
from models import New_Skin
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
    new_user = New_User(data['first_name'], data['last_name'], data['username'], data['email'], data['password'])
    return register_view(new_user)

@app.route('/unique_username', methods=['POST'])
def unique_username():
    data = request.get_json()
    return check_unique_register_input_view('username', data['username'])

@app.route('/unique_email', methods=['POST'])
def unique_email():
    data = request.get_json()
    return check_unique_register_input_view('email', data['email'])

@app.route('/create_session', methods=['GET'])
@login_required_endpoint
def create_session():
    client_ip = request.remote_addr
    return create_session_view(client_ip)

@app.route('/profile', methods=['GET'])
@login_required_endpoint
def profile():
    return profile_view()

@app.route('/game/<game_id>/score_update', methods=['POST'])
@login_required_endpoint
def score_update(game_id):
    data = request.get_json()
    client_ip = request.remote_addr
    client_game_data = Game_Data(data['start_game_token'], data['end_game_token'], data['pointList'])
    return score_update_view(game_id, client_ip, client_game_data, data['score'])

@app.route('/skins', methods=['GET'])
@login_required_page
def skins():
    return skins_view()

@app.route('/skins/get_skin', methods=['POST'])
@login_required_endpoint
def get_skin():
    data = request.get_json()
    skin = Skin(**data['skin'])
    return get_skin_view(data['page'], skin)

@app.route('/skins/select', methods=['POST'])
@login_required_endpoint
def select_skin():
    data = request.get_json()
    return set_user_skin_view(data['skin_id'])

@app.route('/skins/purchase', methods=['POST'])
@login_required_endpoint
def purchase_skin():
    data = request.get_json()
    return purchase_skin_view(data['skin_id'])

@app.route('/create_skin', methods=['GET'])
@admin_page
def create_skin():
    if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
        return redirect('/')
    return create_skin_view()

@app.route('/create_skin', methods=['POST'])
@admin_endpoint
def create_new_skin():
    if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
        abort(403)
    data = request.get_json()
    inputs = [int(x) for x in data['inputs']]
    new_inputs = data['newInputs']
    new_skin = New_Skin(data['skinType'], data['skinHtml'], inputs, new_inputs)
    return create_new_skin_view(new_skin)