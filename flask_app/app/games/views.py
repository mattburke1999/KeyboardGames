from flask import render_template
from app.data_access.models import Func_Result
from app.games.data_access.models import Game_Page

# page
def game_view(game_info: Func_Result, game: str):
    if not game_info.success and type(game_info.result) == dict:
        return render_template(f"{game_info.result['type']}.html", message=game_info.result['message']), game_info.result['type']
    game_page = game_info.result  # type: Game_Page
    if game_page.game_info.basic_circle_template: # type: ignore
        return basic_circle_template(game, game_page) # type: ignore
    return render_template(f'{game}.html', game_page=game_page)

# page
def basic_circle_template(game: str, game_page: Game_Page):
    return render_template('basic_circle_template.html', game=game, game_page=game_page)

    