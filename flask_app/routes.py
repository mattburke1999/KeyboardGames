from flask import Flask
from flask import request
from views import home_view
from views import auth_view
from views import check_unique_register_input_view
from views import register_view
from views import login_view
from views import logout_view
from views import profile_view
from views import login_required_endpoint
from models import New_User

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

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

@app.route('/profile', methods=['GET'])
@login_required_endpoint
def profile():
    return profile_view()