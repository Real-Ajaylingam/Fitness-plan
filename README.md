# FitBuddy — AI Fitness Plan Generator

FitBuddy generates personalized 7-day workout plans and nutrition tips using
Google's Gemini models, built with FastAPI, SQLAlchemy/SQLite, and Jinja2.

## Features

- **Generate a plan** — enter name, user ID, age, weight, goal, and intensity
  to get an AI-generated 7-day workout plan (Gemini Pro) plus a nutrition/
  recovery tip (Gemini Flash).
- **Feedback loop** — submit feedback (e.g. "more cardio", "more rest days")
  to get a revised plan, while the original is preserved.
- **Admin dashboard** — `/view-all-users` lists every user with their original
  and updated plans side by side.

## Project structure

```
fitbuddy/
├── app/
│   ├── main.py                    FastAPI app entrypoint
│   ├── routes.py                  All route handlers
│   ├── database.py                SQLAlchemy models + DB helpers
│   ├── schemas.py                 Pydantic request/response models
│   ├── gemini_generator.py        Gemini Pro: 7-day workout plan
│   ├── gemini_flash_generator.py  Gemini Flash: nutrition tips
│   └── updated_plan.py            Gemini Pro: feedback-based plan revision
├── templates/
│   ├── index.html                 Input form
│   ├── result.html                Plan + tip + feedback form
│   └── all_users.html             Admin dashboard
├── static/
│   └── style.css
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Gemini API key**

   Copy `.env.example` to `.env` and add your key:

   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

   Get a key from [Google AI Studio](https://ai.google.dev/).

   > Note: If `GOOGLE_API_KEY` is not set, FitBuddy still runs — each Gemini
   > call falls back to a simple offline placeholder so you can exercise the
   > full app (forms, storage, admin view) without live credentials.

4. **Run the server**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Open the app**

   - App: http://127.0.0.1:8000
   - Admin dashboard: http://127.0.0.1:8000/view-all-users
   - Interactive API docs: http://127.0.0.1:8000/docs

The SQLite database (`fitbuddy.db`) is created automatically on first run in
the project root.

## Notes

- Uses the current `google-genai` SDK (the older `google-generativeai`
  package was deprecated November 30, 2025). Models default to
  `gemini-3.1-pro-preview` and `gemini-3.5-flash`; override via the
  `GEMINI_PRO_MODEL` / `GEMINI_FLASH_MODEL` env vars. **Do not use
  `gemini-1.5-pro` / `gemini-1.5-flash`** — both are retired and will return
  a 404. Google has also scheduled the `gemini-2.5-pro` / `gemini-2.5-flash`
  line for shutdown on October 16, 2026, so avoid pinning to those long-term
  as well — check https://ai.google.dev/gemini-api/docs/deprecations for the
  current lineup before deploying.
- Feedback updates overwrite the *updated* plan each time but never touch the
  stored *original* plan, so the admin view can always compare both.
