from dataclasses import dataclass
from flask_app.games.models import Game_Info

@dataclass
class New_User:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    
@dataclass
class Func_Result:
    success: bool
    result: any # type: ignore
        
@dataclass
class Profile:
    username: str
    created_time: str
    points: int
    num_top10: int
    ranks: list[dict[str, int|str]]
    
@dataclass
class Home_Page:
    games: list[str]
    game_info: dict[str, Game_Info]
    logged_in: bool


    