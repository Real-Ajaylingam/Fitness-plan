"""
gemini_generator.py
--------------------
Generates a structured 7-day workout plan using Gemini Pro.

Gemini Pro is used here (rather than Flash) because plan generation
benefits from richer, more context-aware, reliably formatted output.
"""

import os
from google import genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")

_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None


def _build_prompt(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    return f"""
You are a certified fitness coach. Create a structured 7-day workout plan for the
following person:

- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Fitness goal: {goal}
- Preferred workout intensity: {intensity}

Format the plan as:
Day 1 - <focus area, e.g. Full Body / Upper Body / Cardio / Rest>
  Warm-up: <5-10 min warm-up description>
  Main workout: <exercise name - sets x reps or duration, for each exercise>
  Cooldown: <brief cooldown / recovery note>

Repeat this structure for Day 1 through Day 7. Keep the plan realistic for the
stated intensity level, vary muscle groups across days, and include at least
one rest or active-recovery day. Keep the entire response plain text, no
markdown headers, no asterisks.
""".strip()


def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    """Call Gemini Pro to produce a 7-day workout plan. Falls back to a
    template plan if no API key is configured or the call fails, so the
    app remains usable without live credentials."""
    prompt = _build_prompt(username, age, weight, goal, intensity)

    if not _client:
        return _fallback_plan(goal, intensity)

    try:
        response = _client.models.generate_content(model=GEMINI_PRO_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # noqa: BLE001 - surface a usable fallback either way
        return f"[Gemini API error: {exc}]\n\n" + _fallback_plan(goal, intensity)


def _fallback_plan(goal: str, intensity: str) -> str:
    """Simple offline placeholder plan, used only when the Gemini API is unavailable."""
    days = ["Full Body", "Upper Body", "Cardio", "Lower Body", "Core & Flexibility", "Active Recovery", "Rest"]
    lines = [f"7-Day Plan (offline placeholder) — Goal: {goal}, Intensity: {intensity}\n"]
    for i, focus in enumerate(days, start=1):
        lines.append(f"Day {i} - {focus}")
        lines.append("  Warm-up: 5-10 min light cardio and dynamic stretching")
        lines.append("  Main workout: 3-4 exercises, 3 sets x 10-12 reps (adjust to intensity)")
        lines.append("  Cooldown: 5 min static stretching")
        lines.append("")
    return "\n".join(lines)
