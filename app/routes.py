from flask import Flask
from views import home as home_view
from views import game_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/<game_name>', methods=['GET'])
def game(game_name):
    return game_view(game_name)