"""
gemini_flash_generator.py
--------------------------
Generates a short, practical nutrition/recovery tip using Gemini Flash.

Flash is used here instead of Pro because this call is small, latency
sensitive, and doesn't need Pro's deeper reasoning.
"""

import os
from google import genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.5-flash")

_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """Call Gemini Flash for a concise nutrition/recovery tip tied to the user's goal."""
    prompt = (
        f"Give one concise, practical nutrition or recovery tip (2-3 sentences max) "
        f"for someone whose fitness goal is '{goal}'. Be specific and actionable. "
        f"Plain text only, no markdown."
    )

    if not _client:
        return _fallback_tip(goal)

    try:
        response = _client.models.generate_content(model=GEMINI_FLASH_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as exc:  # noqa: BLE001
        return f"[Gemini API error: {exc}] " + _fallback_tip(goal)


def _fallback_tip(goal: str) -> str:
    tips = {
        "weight loss": "Prioritize protein and fiber at each meal to stay full longer, "
                       "and keep a modest calorie deficit rather than an extreme one.",
        "muscle gain": "Include protein in your post-workout meal (chicken, fish, beans, "
                       "or Greek yogurt) to support muscle repair and growth.",
        "general wellness": "Stay hydrated throughout the day and aim for a colorful "
                             "variety of vegetables to cover your micronutrient bases.",
    }
    return tips.get(goal.lower(), "Eat a balanced meal with protein, complex carbs, "
                                   "and healthy fats within two hours after training.")
