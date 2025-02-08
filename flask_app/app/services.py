from app.data_access.models import Func_Result
from app.data_access.models import Home_Page

from app.games.services import get_games_process
from app.auth.services import check_login



def get_home_page_data() -> Func_Result:
    games = get_games_process()
    if not games.success or not games.result:
        return Func_Result(False, None)
    logged_in = check_login()
    print(f'service logged_in: {logged_in}')
    return Func_Result(True, Home_Page(games.result, logged_in))


