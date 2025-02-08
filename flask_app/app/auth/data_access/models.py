from dataclasses import dataclass
from datetime import datetime

@dataclass
class New_User:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    