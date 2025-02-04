from dataclasses import dataclass
from app.games.models import Game_Info
 
@dataclass
class Func_Result:
    success: bool
    result: any # type: ignore
    
@dataclass
class Home_Page:
    games: list[str]
    game_info: dict[str, Game_Info]
    logged_in: bool


    