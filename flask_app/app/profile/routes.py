from flask import Blueprint
from app.views import json_result
from app.profile.services import get_profile
from app.utils.route_decorators import login_required

bp = Blueprint('profile', __name__, url_prefix='/profile', template_folder='templates', static_folder='static')

@bp.route('/', methods=['GET'])
@login_required('api')
def profile():
    result = get_profile()
    return json_result(result)