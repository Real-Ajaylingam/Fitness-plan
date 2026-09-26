"""
schemas.py
----------
Pydantic models used to validate incoming form/API data.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserInput(BaseModel):
    user_id: str = Field(..., description="Unique identifier chosen by the user")
    username: str
    age: int = Field(..., gt=0, lt=120)
    weight: float = Field(..., gt=0)
    goal: str = Field(..., description="e.g. weight loss, muscle gain, general wellness")
    intensity: str = Field(..., description="low, medium, or high")


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str


class PlanResponse(BaseModel):
    username: str
    user_id: str
    age: int
    weight: float
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    updated_plan: Optional[str] = None
