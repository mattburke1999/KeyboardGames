from flask import Flask
from views import home as home_view
from views import first_circle as first_circle_view
from views import second_circle as second_circle_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()

@app.route('/firstCircle', methods=['GET'])
def first_circle():
    return first_circle_view()

@app.route('/secondCircle', methods=['GET'])
def second_circle():
    return second_circle_view()