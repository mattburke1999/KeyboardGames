from flask import Flask
from app.views import home_view
from app.services import get_home_page_data

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    home_page = get_home_page_data()
    return home_view(home_page)

