from dataclasses import dataclass

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
class Skin_Input:
    id: int
    name: str

@dataclass
class Skin_Type_With_Inputs:
    id: int
    name: str
    inputs: list[str]

@dataclass
class Skins_Page:
    points: int
    skins: list[Skin]
    
    def __init__(self, points: int, skins: list[dict]):
        self.points = points
        self.skins = sorted([Skin(**skin) for skin in skins], key=lambda x: (x.points, x.type, x.id))
    
@dataclass
class New_Skin_Type:
    type: str
    inputs: list[int]
    new_inputs: list[str]
    html: str | None = None

@dataclass
class New_Skin_Input:
    type_id: int
    inputs: dict[str, str|dict[str, list[str]|int]]
    points: int  
    names: str | None = None
    mapper_json: str | None = None  
    
@dataclass
class Create_Skin_Page:
    inputs: list[Skin_Input]
    types: list[Skin_Type_With_Inputs]