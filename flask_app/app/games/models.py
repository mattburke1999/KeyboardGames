from dataclasses import dataclass
from app.skins.models import Skin

@dataclass
class Game_Info:
    id: int
    title: str
    title_style: str
    title_color: str
    bg_rot: int
    bg_color1: str
    bg_color2: str
    duration: int
    basic_circle_template: str

@dataclass
class Game_Page:
    game_info: Game_Info
    logged_in: bool
    ip: str
    user_skin: Skin
    
@dataclass
class Game_Data:
    start_game_token: str
    end_game_token: str
    point_list: list[dict[str, str]]

@dataclass
class Top10_Score:
    username: str
    score: int
    date: str
    current_score: bool
    
@dataclass
class Top3_Score:
    score: int
    date: str
    current_score: bool

@dataclass
class Score_View:
    top10: list[Top10_Score]
    top3: list[Top3_Score]
    points_added: int
    score_rank: int