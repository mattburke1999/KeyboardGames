from flask import render_template
from services import get_home_page_data
from services import get_game_info

def home():
    home_page_results = get_home_page_data()
    return render_template('index.html', games=home_page_results[1]['games'], game_info=home_page_results[1]['game_info'], logged_in=home_page_results[1]['logged_in'])

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