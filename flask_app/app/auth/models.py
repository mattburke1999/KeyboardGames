from dataclasses import dataclass

@dataclass
class New_User:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    
@dataclass
class Profile:
    username: str
    created_time: str
    points: int
    num_top10: int
    ranks: list[dict[str, int|str]]