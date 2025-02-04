from models import Func_Result
from models import Home_Page
import socket

from flask_app.games.services import get_games
from flask_app.auth.services import check_login

GAME_INFO = {}
GAMES = []

def get_home_page_data() -> Func_Result:
    games = get_games()
    if not games.success or not games.result:
        return Func_Result(False, None)
    logged_in = check_login()
    print(f'service logged_in: {logged_in}')
    return Func_Result(True, Home_Page(games.result[1], games.result[0], logged_in))

def get_server_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

