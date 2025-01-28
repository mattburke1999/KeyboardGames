from dataclasses import dataclass

@dataclass
class NewUser:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    
@dataclass
class DB_Result:
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
class Skin:
    type: str
    name: str
    data: dict[str, str]
    id: int | None = None
    points: int | None = None
    user_choice: bool | None = None
    user_skin: bool | None = None

@dataclass
class Skins_Page:
    points: int
    skins: list[Skin]
    
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
class Home_Page:
    games: list[str]
    game_info: dict[str, Game_Info]
    logged_in: bool
    
@dataclass
class Game_Data:
    start_game_token: str
    end_game_token: str
    point_list: list[dict[str, any]] # type: ignore

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


    