from dataclasses import dataclass
from app.games.data_access.models import Game_Info
 
@dataclass
class Func_Result:
    success: bool
    result: any # type: ignore
    
@dataclass
class Home_Page:
    games: list[str]
    game_info: dict[str, Game_Info]
    logged_in: bool
    
    def __init__(self, game_info: dict[str, Game_Info], logged_in: bool):
        self.games = list(game_info.keys())
        self.game_info = game_info
        self.logged_in = logged_in


    