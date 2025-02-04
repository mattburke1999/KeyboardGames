from flask import Flask
from app.views import home_view

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return home_view()