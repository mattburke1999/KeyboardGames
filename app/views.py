from flask import render_template
from services import get_games
from services import get_game_info

def home():
    game_results = get_games()
    return render_template('index.html', games=game_results[1][1], game_info=game_results[1][0])

def game_view(game):
    game_info_results = get_game_info(game)
    game_info = game_info_results[1]['game_info']
    if not game_info:
        return render_template('404.html'), 404
    if game_info['basic_circle_template']:
        return basic_circle_template(game, game_info)
    return render_template(f'{game}.html', game_info=game_info)

def basic_circle_template(game, game_info):
    return render_template('basic_circle_template.html', game=game, game_info=game_info)

def login_view(page):
    return render_template('login.html', page=page)