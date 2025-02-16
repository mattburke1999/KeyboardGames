from dataclasses import dataclass
from datetime import datetime

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