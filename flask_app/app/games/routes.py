from flask import Blueprint
from flask import request
from app.games.services import get_game_page
from app.games.services import create_session_process
from app.games.services import score_update_process
from app.games.views import game_view
from app.views import json_result
from app.utils.route_decorators import login_required
from app.utils.route_decorators import require_json
from app.utils.route_decorators import get_client_ip

bp = Blueprint('games', __name__, url_prefix='/games', template_folder='templates', static_folder='static')

@bp.route('/<game_name>', methods=['GET']) # type: ignore
def game(game_name: str):
    game_info = get_game_page(game_name)
    return game_view(game_info, game_name)

@bp.route('/create_session', methods=['GET'])
@login_required('api')
@get_client_ip
def create_session(client_ip):
    result = create_session_process(client_ip)
    return json_result(result)

@bp.route('/<game_id>/score_update', methods=['POST'])
@login_required('api')
@get_client_ip
@require_json
def score_update(game_id, client_ip, data):
    result = score_update_process(client_ip, data, game_id)
    return json_result(result)