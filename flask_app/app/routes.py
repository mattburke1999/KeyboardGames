from flask import Flask
from app.views import home_view
from app.views import json_result
from app.services import get_home_page_data
from app.services import get_profile
from app.utils.route_decorators import login_required

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    home_page = get_home_page_data()
    return home_view(home_page)

@app.route('/profile', methods=['GET'])
@login_required('api')
def profile():
    result = get_profile()
    return json_result(result)