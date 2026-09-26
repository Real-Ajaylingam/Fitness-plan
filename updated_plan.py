"""
updated_plan.py
----------------
Revises an existing workout plan based on free-text user feedback,
using Gemini Pro.
"""

import os
from google import genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")

_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None


def update_workout_plan(original_plan: str, feedback: str) -> str:
    """Send the original plan + user feedback to Gemini Pro and return a revised plan."""
    prompt = f"""
Here is a user's current 7-day workout plan:

{original_plan}

The user has given this feedback: "{feedback}"

Revise the 7-day plan to incorporate this feedback while keeping the same
day-by-day structure (Day 1 through Day 7, each with Warm-up, Main workout,
Cooldown). Keep the response plain text, no markdown headers, no asterisks.
""".strip()

    if not _client:
        return _fallback_update(original_plan, feedback)

    try:
        response = _client.models.generate_content(model=GEMINI_PRO_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # noqa: BLE001
        return f"[Gemini API error: {exc}]\n\n" + _fallback_update(original_plan, feedback)


def _fallback_update(original_plan: str, feedback: str) -> str:
    """Offline placeholder: appends the feedback as a note rather than truly revising the plan."""
    return (
        f"{original_plan}\n\n"
        f"--- Note: could not reach Gemini API to fully apply your feedback ---\n"
        f"Feedback received: \"{feedback}\" (please retry once GOOGLE_API_KEY is configured)"
    )
