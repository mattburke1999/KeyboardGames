from dataclasses import dataclass
from app.skins.models import Skin
from datetime import datetime

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
    
    def __init__(self, high_scores: list[dict], points_added: int, score_rank: int):
        self.top10 = [Top10_Score(hs['username'], hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
            for hs in high_scores if hs['score_type'] == 'top10']
        self.top3 = [Top3_Score(hs['score'], datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'), hs['current_score'])
            for hs in high_scores if hs['score_type'] == 'top3']
        self.points_added = points_added
        self.score_rank = score_rank