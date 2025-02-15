from flask import Blueprint
from flask import request
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
from app.utils.route_decorators import login_required
from app.utils.route_decorators import admin_only
from app.utils.route_decorators import localhost_only
from app.utils.route_decorators import require_json

bp = Blueprint('skins', __name__, url_prefix='/skins', template_folder='templates', static_folder='static')

@bp.route('/', methods=['GET'])
@login_required('page')
def skins():
    skins_page = get_all_skins()
    return skins_view(skins_page)

@bp.route('/get_skin', methods=['POST'])
@login_required('api')
@require_json
def get_skin(data):
    return get_skin_view(data)

@bp.route('/select', methods=['POST'])
@login_required('api')
@require_json
def select_skin(data):
    result = set_user_skin(data)
    return json_result(result)

@bp.route('/purchase', methods=['POST'])
@login_required('api')
@require_json
def purchase_skin(data):
    result = purchase_skin_s(data)
    return json_result(result)

@bp.route('/create_skin', methods=['GET'])
@localhost_only('page')
@admin_only('page')
def create_skin():
    create_skin = create_skin_page()
    return create_skin_view(create_skin)

@bp.route('/create_skin_type', methods=['POST'])
@localhost_only('api')
@admin_only('api')
@require_json
def create_new_skin_type(data):
    result = create_new_skin_type_s(data)
    return json_result(result)

@bp.route('/create_skin_inputs', methods=['POST'])
@localhost_only('api')
@admin_only('api')
@require_json
def create_skin_inputs(data):
    result = create_new_skin_input(data)
    return json_result(result)