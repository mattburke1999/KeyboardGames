from db import get_games as db_get_games

GAME_INFO = {}
GAMES = []

def get_games():
    global GAME_INFO
    global GAMES
    if len(GAMES) == 0:
        game_results = db_get_games()
        print(game_results)
        if not game_results[0]:
            return (False, None)
        for game in game_results[1]:
            GAMES.append(game[7])
            GAME_INFO[game[7]] = {
                'id': game[0],
                'title': game[1],
                'title_style': game[2],
                'title_color': game[3],
                'bg_rot': game[4],
                'bg_color1': game[5],
                'bg_color2': game[6],
                'duration': game[8],
                'basic_circle_template': game[9]
            }
    return (True, (GAME_INFO, GAMES))

def get_game_info(game):
    if not GAME_INFO:
        games_result = get_games()
        if not games_result[0]:
            return (False, None)
    if game not in GAME_INFO:
        return (True, {'game_info': None})
    return (True, {'game_info': GAME_INFO[game]})