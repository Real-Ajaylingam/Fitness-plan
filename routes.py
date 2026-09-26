"""
routes.py
---------
Core routing layer for FitBuddy. Bridges the frontend templates, the
Gemini-powered generation functions, and the SQLite database.

Routes:
  GET  /                 -> home page (input form)
  POST /generate-workout -> generate & store a 7-day plan + nutrition tip
  POST /submit-feedback  -> revise an existing plan based on feedback
  GET  /view-all-users   -> admin dashboard of all users and plans
"""

import os
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    save_user,
    save_plan,
    update_plan,
    get_user,
    get_original_plan,
    get_all_users,
    get_all_plans,
)
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/")
def home(request: Request):
    """Scenario entry point: show the user input form."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate-workout")
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    """Scenario 1: generate a personalized 7-day workout plan + nutrition tip."""
    workout_plan = generate_workout_gemini(username, age, weight, goal, intensity)
    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    save_user(db, user_id, username, age, int(weight), goal, intensity)
    save_plan(db, user_id, workout_plan, nutrition_tip)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": None,
            "feedback_confirmation": None,
        },
    )


@router.post("/submit-feedback")
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    """Scenario 2: revise an existing plan based on user feedback."""
    user = get_user(db, user_id)
    original = get_original_plan(db, user_id)

    if not user or not original:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "username": "Unknown",
                "user_id": user_id,
                "age": "-",
                "weight": "-",
                "goal": "-",
                "intensity": "-",
                "workout_plan": "No existing plan found for this User ID. "
                                "Please generate a plan first.",
                "nutrition_tip": "",
                "updated_plan": None,
                "feedback_confirmation": None,
            },
        )

    revised_plan = update_workout_plan(original, feedback)
    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    update_plan(db, user_id, revised_plan, nutrition_tip)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": original,
            "nutrition_tip": nutrition_tip,
            "updated_plan": revised_plan,
            "feedback_confirmation": "Your plan has been updated based on your feedback!",
        },
    )


@router.get("/view-all-users")
def view_all_users(request: Request, db: Session = Depends(get_db)):
    """Scenario 4: admin dashboard listing every user and their plans."""
    users = get_all_users(db)
    plans = get_all_plans(db)

    plans_by_user_id = {plan.user_id: plan for plan in plans}
    rows = []
    for user in users:
        plan = plans_by_user_id.get(user.user_id)
        rows.append(
            {
                "user": user,
                "original_plan": plan.original_plan if plan else None,
                "updated_plan": plan.updated_plan if plan else None,
                "nutrition_tip": plan.nutrition_tip if plan else None,
            }
        )

    return templates.TemplateResponse("all_users.html", {"request": request, "rows": rows})
