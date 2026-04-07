# Sereni – AI-Driven Sentiment Analysis Chatbot

## Overview
Sereni is a Flask + vanilla JS application providing empathetic chat with real-time sentiment, risk detection, and grounding support. Architecture separates routes, services, AI modules, and frontend.

## Setup
1) Python 3.11 recommended.
2) `python -m venv .venv && .venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Unix).
3) `pip install -r requirements.txt`
4) Download VADER lexicon once (offline-friendly): `python -m nltk.downloader vader_lexicon`
5) Set env vars: `SERENI_SECRET_KEY`, `DATABASE_URL` (optional), `SERENI_API_TOKEN` (optional).
6) `flask --app backend.app --env-file .env run` for dev.

## Architecture
- `backend/app.py`: Flask factory, extension wiring.
- `backend/routes`: request/response only; delegates to services. UI routes under `ui.py`, APIs under `api.py`.
- `backend/services`: business logic (chat, analytics, grounding).
- `backend/ai`: self-contained NLP/risk modules (VADER today, replaceable with transformers).
- `backend/auth`: Flask-Login + CSRF protected forms.
- `frontend`: HTML/CSS/JS (no frameworks) with glassmorphism UI.

## API (prefix /api)
- `POST /api/chat` → {response, sentiment, risk, confidence}
- `POST /api/analyze` → raw features/scores
- `GET /api/emergency` → helpline list
All JSON; include `Authorization: Bearer <SERENI_API_TOKEN>` if configured.

## UI
- `GET /chat` (and `/`) renders the chat interface.

## Ethical Considerations
- Non-clinical language; encourages professional help.
- Crisis helplines surfaced; high-risk prompts suggest escalation.
- Input sanitization, rate limiting, and CSRF on forms.

## Testing
`pytest` (CSRF disabled in tests).

## Deployment
Use `Dockerfile` with Gunicorn entry `wsgi:app`. Configure env vars and persistent database volume.
