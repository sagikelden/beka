from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Team(BaseModel):
    id: str
    name: str

class Match(BaseModel):
    id: Optional[str]
    home: Team
    away: Team
    start_time: datetime
    status: str = "scheduled"  # scheduled|live|finished
    score: Optional[dict] = {"home": 0, "away": 0}
