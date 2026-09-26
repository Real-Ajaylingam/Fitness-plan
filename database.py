"""
database.py
-----------
SQLite persistence layer for FitBuddy, using SQLAlchemy ORM.

Stores:
- User: personal details (name, user_id, age, weight, goal, intensity)
- Plan: the original AI-generated workout plan, the current nutrition tip,
  and (optionally) an updated plan produced from user feedback.

Both original and updated plans are preserved so the admin dashboard can
show how a user's plan evolved.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)

    plan = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)

    user = relationship("User", back_populates="plan")


def init_db():
    """Create tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helper functions used directly by routes.py
# ---------------------------------------------------------------------------

def save_user(db, user_id: str, username: str, age: int, weight: int, goal: str, intensity: str) -> User:
    """Create a new user record, or update it if the user_id already exists."""
    existing = db.query(User).filter(User.user_id == user_id).first()
    if existing:
        existing.username = username
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing.intensity = intensity
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        user_id=user_id,
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def save_plan(db, user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    """Store the freshly generated workout plan and nutrition tip for a user."""
    existing = db.query(Plan).filter(Plan.user_id == user_id).first()
    if existing:
        existing.original_plan = original_plan
        existing.nutrition_tip = nutrition_tip
        existing.updated_plan = None  # reset any previous feedback-based update
        db.commit()
        db.refresh(existing)
        return existing

    plan = Plan(user_id=user_id, original_plan=original_plan, nutrition_tip=nutrition_tip)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_original_plan(db, user_id: str) -> str | None:
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    return plan.original_plan if plan else None


def update_plan(db, user_id: str, updated_plan_text: str, nutrition_tip: str | None = None) -> Plan | None:
    """Persist a revised plan (from the feedback loop) alongside the original."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if not plan:
        return None
    plan.updated_plan = updated_plan_text
    if nutrition_tip:
        plan.nutrition_tip = nutrition_tip
    db.commit()
    db.refresh(plan)
    return plan


def get_all_users(db) -> list[User]:
    return db.query(User).all()


def get_all_plans(db) -> list[Plan]:
    return db.query(Plan).all()
