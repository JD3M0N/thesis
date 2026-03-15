# Backend Map

## Entrypoints

- App factory: `backend/app/main.py`
- Settings: `backend/app/config.py`
- DB setup: `backend/app/database.py`
- Auth routes: `backend/app/routers/auth.py`
- Story routes: `backend/app/routers/stories.py`
- Pipeline runner: `backend/app/services/orchestrator.py`
- Agent prompts: `backend/app/services/agents.py`
- Gemini client: `backend/app/services/gemini.py`
- Backend tests: `backend/tests/test_api.py`

## Source of truth order

1. `backend/app/schemas.py` for payload shapes and `StoryPacket`
2. `backend/app/models.py` for persistence fields
3. `backend/app/routers/*.py` for HTTP behavior
4. `backend/app/services/*.py` for orchestration and LLM behavior
5. `backend/tests/test_api.py` for expected behavior

## Commands

- Install backend deps: `cd backend && pip install -e .[dev]`
- Run API: `cd backend && uvicorn app.main:app --reload --port 8000`
- Run tests: `cd backend && pytest`

## Task routing

- Prompt changes, pipeline ordering, retries, worker flow, auth, DB fields, or route logic stay in this skill.
- Shared request/response or status changes must switch to `story-contract-sync`.
