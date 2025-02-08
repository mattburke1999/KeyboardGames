from dataclasses import dataclass
from app.games.data_access.models import Game_Info
from datetime import datetime
 
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
        
@dataclass
class Profile:
    username: str
    created_time: str
    points: int
    num_top10: int
    ranks: list[dict[str, int|str]]
    
    def __init__(self, username: str, created_time: datetime, points: int, num_top10: int, ranks: list[dict[str, int|str]]):
        self.username = username
        self.created_time = created_time.strftime('%m/%d/%Y')
        self.points = points
        self.num_top10 = num_top10
        self.ranks = sorted(ranks, key=lambda x: (x['rank'], x['game_name']))


    