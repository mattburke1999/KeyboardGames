from flask import Blueprint
from flask import request
from flask import redirect
from flask import abort
from app.views import json_result
from app.skins.views import skins_view
from app.skins.views import get_skin_view
from app.skins.views import create_skin_view
from app.skins.services import get_all_skins
from app.skins.services import set_user_skin
from app.skins.services import purchase_skin as purchase_skin_s
from app.skins.services import create_skin_page
from app.skins.services import create_new_skin_type as create_new_skin_type_s
from app.skins.services import create_new_skin_input

bp = Blueprint('skins', __name__, url_prefix='/skins')

@bp.route('/', methods=['GET'])
#@login_required_page
def skins():
    skins_page = get_all_skins()
    return skins_view(skins_page)

@bp.route('/get_skin', methods=['POST'])
#@login_required_endpoint
def get_skin():
    data = request.get_json()
    return get_skin_view(data)

@bp.route('/select', methods=['POST'])
#@login_required_endpoint
def select_skin():
    data = request.get_json()
    result = set_user_skin(data)
    return json_result(result)

@bp.route('/purchase', methods=['POST'])
#@login_required_endpoint
def purchase_skin():
    data = request.get_json()
    result = purchase_skin_s(data)
    return json_result(result)

@bp.route('/create_skin', methods=['GET'])
# @admin_page
def create_skin():
    if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
        return redirect('/') # change to redirect to flask_app.routes.home
    create_skin = create_skin_page()
    return create_skin_view(create_skin)

@bp.route('/create_skin_type', methods=['POST'])
# @admin_endpoint
def create_new_skin_type():
    if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
        abort(403)
    data = request.get_json()
    result = create_new_skin_type_s(data)
    return json_result(result)

@bp.route('/create_skin_inputs', methods=['POST'])
# @admin_endpoint
def create_skin_inputs():
    if request.host != 'localhost:5000' and '127.0.0.1:5000' not in request.host:
        abort(403)
    data = request.get_json()
    result = create_new_skin_input(data)
    return json_result(result)