from flask import Flask
from views import home as home_view
from views import first_circle as first_circle_view
from views import second_circle as second_circle_view
from views import disappearing_circle as disappearing_circle_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/games/the-first-one', methods=['GET'])
def first_circle():
    return first_circle_view()

@app.route('/games/gotta-move-quickly', methods=['GET'])
def second_circle():
    return second_circle_view()

@app.route('/games/disappearing-circle', methods=['GET'])
def disappearing_circle():
    return disappearing_circle_view()