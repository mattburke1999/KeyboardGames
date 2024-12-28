from flask import Flask
from views import home as home_view
from views import game_view
from views import login_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/<game_name>', methods=['GET'])
def game(game_name):
    return game_view(game_name)

@app.route('/login', methods=['GET'])
def login():
    return login_view('login')

@app.route('/register', methods=['GET'])
def register():
    return login_view('register')