from flask import Flask
from views import home as home_view
from views import game_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/the-first-one', methods=['GET'])
def first_one():
    return game_view('first_one')

@app.route('/games/gotta-move-fast', methods=['GET'])
def gotta_move_fast():
    return game_view('gotta_move_fast')

@app.route('/games/disappearing-circles', methods=['GET'])
def disappearing_circles():
    return game_view('disappearing_circles')

@app.route('/games/disappearing-dot', methods=['GET'])
def disappearing_dot():
    return game_view('disappearing_dot')

@app.route('/games/shrinking-circles', methods=['GET'])
def shrinking_circles():
    return game_view('shrinking_circles')