from flask import Blueprint
from flask import request
from app.games.services import get_game_info
from app.games.services import create_session as create_session_s
from app.games.services import score_update as score_update_s
from app.games.views import game_view
from app.views import json_result

bp = Blueprint('games', __name__, url_prefix='/games')

@bp.route('/<game_name>', methods=['GET']) # type: ignore
def game(game_name: str):
    game_info = get_game_info(game_name)
    return game_view(game_info, game_name)

@bp.route('/create_session', methods=['GET'])
# @login_required_endpoint
def create_session():
    client_ip = request.remote_addr
    result = create_session_s(client_ip)
    return json_result(result)

@bp.route('/<game_id>/score_update', methods=['POST'])
# @login_required_endpoint
def score_update(game_id):
    data = request.get_json()
    client_ip = request.remote_addr
    result = score_update_s(client_ip, data, game_id)
    return json_result(result)