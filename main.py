"""
main.py
-------
FitBuddy application entrypoint. Loads environment variables, initializes
the database, mounts static files, and wires up the router.

Run with:
    uvicorn app.main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from app.database import init_db
from app.routes import router

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(router)


@app.on_event("startup")
def on_startup():
    init_db()
