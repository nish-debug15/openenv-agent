from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# What agent sees
class Observation(BaseModel):
    symptoms: List[str]
    pain_level: int
    age: int
    step: int
    hidden_info: Optional[List[str]] = []

# What agent does
class Action(BaseModel):
    action_type: str
    content: str

# Reward model
class Reward(BaseModel):
    reward: float
    done: bool
    info: Dict[str, Any]